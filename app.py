import os
import uuid
import traceback
from functools import wraps

import bcrypt
import pyodbc
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from utils.ocr_processor import OCRProcessor
from features.ocr.managers.customers import CustomerManager
from features.ocr.managers.containers import ContainerManager
from features.ocr.managers.services import ServiceManager
from features.ocr.managers.receipts import ReceiptManager
from features.ocr.managers.lines import LineManager
from utils.db_helper import get_db_connection
from features.customers_count.count_service import CustomerCountService
from features.documents_count.count_service import DocumentCountService
from features.visits_count.count_service import VisitCountService
from features.customer_search.search_service import CustomerSearchService
from features.user_management.role_service import RoleService
from features.user_management.user_service import UserService
from features.user_management.department_service import DepartmentService
from features.dashboard_report.report_service import DashboardReportService

app = Flask(__name__)
# Sử dụng environment variable cho secret key, fallback về random key nếu không có
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 86400

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        username = session.get("username")
        if not username:
            return redirect(url_for("login"))
        user_service = UserService()
        if not user_service.is_admin(username):
            flash("Bạn không có quyền truy cập trang này!", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Vui lòng điền đầy đủ thông tin!", "error")
            return render_template("login.html")
        
        conn = get_db_connection()
        if not conn:
            flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
            return render_template("login.html")
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            
            cursor.execute(
                """SELECT u.user_name, u.pass_word, u.email, u.phone_number, u.first_name, u.middle_name, u.last_name, r.role_name, d.department
                   FROM dbo.users u WITH (READPAST)
                   LEFT JOIN dbo.roles r ON u.role_key = r.role_key
                   LEFT JOIN dbo.departments d ON u.department_key = d.department_key
                   WHERE LOWER(u.user_name) = LOWER(?)""",
                (username,)
            )
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
                session["user_id"] = user[0]
                session["username"] = user[0]
                session["email"] = user[2]
                session["phone_number"] = user[3]
                session["first_name"] = user[4] if user[4] else ""
                session["middle_name"] = user[5] if user[5] else ""
                session["last_name"] = user[6] if user[6] else ""
                session["role"] = user[7] if user[7] else None
                session["department"] = user[8] if user[8] else ""
                session["session_tracking_id"] = str(uuid.uuid4())
                
                conn.commit()
                conn.close()
                
                return redirect(url_for("home"))
            else:
                conn.rollback()
                flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
        except Exception as e:
            print(f"Lỗi đăng nhập: {e}")
            try:
                conn.rollback()
            except:
                pass
            flash("Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.", "error")
        finally:
            try:
                conn.close()
            except:
                pass
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))
    
    user_service = UserService()
    role_service = RoleService()
    department_service = DepartmentService()
    has_users = user_service.has_any_users()
    
    if has_users:
        available_roles = role_service.get_roles_for_registration()
    else:
        available_roles = role_service.get_all_roles()
    
    departments = department_service.get_all_departments()
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        department_key = request.form.get("department_key", "").strip()
        
        if not has_users:
            role_name = "ADMIN"
        else:
            role_name = request.form.get("role", "").strip()
        
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirmPassword", "")
        
        if not username or not email or not phone_number or not first_name or not last_name or not password or not confirm_password:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if has_users and not role_name:
            flash("Vui lòng chọn vai trò!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if has_users and role_name.upper() == "ADMIN":
            flash("Không thể tạo tài khoản ADMIN! Chỉ có thể tạo ADMIN lần đầu.", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        role_key = role_service.get_role_key_by_name(role_name)
        if not role_key:
            flash("Vai trò không hợp lệ!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if department_key:
            dept = department_service.get_all_departments()
            dept_dict = {d["department_key"]: d for d in dept}
            if department_key not in dept_dict:
                department_key = None
        
        if phone_number.startswith("+84"):
            phone_number = "0" + phone_number[3:]
        phone_number = "".join(filter(str.isdigit, phone_number))
        
        if not phone_number.startswith("0") or len(phone_number) != 10:
            flash("Số điện thoại không hợp lệ! Phải có 10 số và bắt đầu bằng 0.", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if "@" not in email or "." not in email.split("@")[1]:
            flash("Email không hợp lệ!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if len(password) < 8:
            flash("Mật khẩu phải có ít nhất 8 ký tự!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if not any(c.islower() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ cái viết thường!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if not any(c.isupper() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ cái viết in hoa!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if not any(c.isdigit() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ số!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        special_chars = "!@#$%^&*()_+-=[]{};:\"'\\|,.<>/?"
        if not any(c in special_chars for c in password):
            flash("Mật khẩu phải có ít nhất 1 ký tự đặc biệt!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp!", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        conn = get_db_connection()
        if not conn:
            flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
            return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            cursor.execute(
                "SELECT user_name FROM dbo.users WITH (UPDLOCK, HOLDLOCK) WHERE LOWER(user_name) = LOWER(?)",
                (username,)
            )
            if cursor.fetchone():
                conn.rollback()
                conn.close()
                flash("Tên đăng nhập đã tồn tại! Vui lòng chọn tên đăng nhập khác.", "error")
                return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
            
            cursor.execute(
                "SELECT email FROM dbo.users WITH (UPDLOCK, HOLDLOCK) WHERE LOWER(email) = LOWER(?)",
                (email,)
            )
            if cursor.fetchone():
                conn.rollback()
                conn.close()
                flash("Email đã được sử dụng! Vui lòng sử dụng email khác.", "error")
                return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
            
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            try:
                if department_key:
                    cursor.execute(
                        "INSERT INTO dbo.users (user_name, pass_word, email, phone_number, role_key, first_name, middle_name, last_name, department_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (username, hashed_password, email, phone_number, role_key, first_name, middle_name or None, last_name, department_key)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO dbo.users (user_name, pass_word, email, phone_number, role_key, first_name, middle_name, last_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (username, hashed_password, email, phone_number, role_key, first_name, middle_name or None, last_name)
                    )
                conn.commit()
                flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                conn.close()
                return redirect(url_for("login"))
            except pyodbc.IntegrityError as ie:
                conn.rollback()
                conn.close()
                error_msg = str(ie).lower()
                if "user_name" in error_msg or "primary key" in error_msg:
                    flash("Tên đăng nhập đã tồn tại! Vui lòng chọn tên đăng nhập khác.", "error")
                elif "email" in error_msg or "unique" in error_msg:
                    flash("Email đã được sử dụng! Vui lòng sử dụng email khác.", "error")
                else:
                    flash("Thông tin đã tồn tại! Vui lòng kiểm tra lại.", "error")
                return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)
            
        except Exception as e:
            print(f"Lỗi đăng ký: {e}")
            try:
                conn.rollback()
            except:
                pass
            flash("Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.", "error")
        finally:
            try:
                conn.close()
            except:
                pass
    
    return render_template("register.html", roles=available_roles, departments=departments, is_first_user=not has_users)

@app.route("/home")
@login_required
def home():
    username = session.get("username")
    if username:
        visit_service = VisitCountService()
        session_tracking_id = session.get("session_tracking_id")
        if session_tracking_id:
            visit_service.record_visit(session_tracking_id)
    
    user_service = UserService()
    is_admin = user_service.is_admin(username) if username else False
    user_role = session.get("role") or "N/A"
    
    # Lấy họ tên đầy đủ từ database
    full_name = username  # Mặc định là username nếu không tìm thấy
    if username:
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT first_name, middle_name, last_name FROM dbo.users WHERE user_name = ?",
                    (username,)
                )
                user_info = cursor.fetchone()
                conn.close()
                
                if user_info:
                    first_name = user_info[0] if user_info[0] else ""
                    middle_name = user_info[1] if user_info[1] else ""
                    last_name = user_info[2] if user_info[2] else ""
                    # Ghép họ tên đầy đủ
                    name_parts = [part for part in [first_name, middle_name, last_name] if part]
                    full_name = " ".join(name_parts) if name_parts else username
        except Exception as e:
            print(f"Lỗi lấy họ tên đầy đủ: {e}")
            full_name = username
    
    return render_template(
        "dashboard.html", 
        username=username,
        full_name=full_name,
        email=session.get("email"),
        phone_number=session.get("phone_number"),
        is_admin=is_admin,
        user_role=user_role
    )

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if "user_id" in session:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        
        if not username:
            flash("Vui lòng nhập tên đăng nhập!", "error")
            return render_template("forgot-password.html")
        
        conn = get_db_connection()
        if not conn:
            flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
            return render_template("forgot-password.html")
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_name FROM dbo.users WHERE LOWER(user_name) = LOWER(?)",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                flash("Tên đăng nhập không tồn tại!", "error")
                conn.close()
                return render_template("forgot-password.html")
            
            session["reset_username"] = user[0]
            conn.close()
            return redirect(url_for("reset_password"))
            
        except Exception as e:
            print(f"Lỗi kiểm tra username: {e}")
            flash("Có lỗi xảy ra. Vui lòng thử lại.", "error")
            conn.close()
    
    return render_template("forgot-password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "user_id" in session:
        return redirect(url_for("home"))
    
    username = session.get("reset_username")
    if not username:
        flash("Vui lòng nhập tên đăng nhập trước!", "error")
        return redirect(url_for("forgot_password"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirmPassword", "")
        
        if not password or not confirm_password:
            flash("Vui lòng điền đầy đủ thông tin!", "error")
            return render_template("reset-password.html", username=username)
        
        if len(password) < 8:
            flash("Mật khẩu phải có ít nhất 8 ký tự!", "error")
            return render_template("reset-password.html", username=username)
        
        if not any(c.islower() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ cái viết thường!", "error")
            return render_template("reset-password.html", username=username)
        
        if not any(c.isupper() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ cái viết in hoa!", "error")
            return render_template("reset-password.html", username=username)
        
        if not any(c.isdigit() for c in password):
            flash("Mật khẩu phải có ít nhất 1 chữ số!", "error")
            return render_template("reset-password.html", username=username)
        
        special_chars = "!@#$%^&*()_+-=[]{};:\"'\\|,.<>/?"
        if not any(c in special_chars for c in password):
            flash("Mật khẩu phải có ít nhất 1 ký tự đặc biệt!", "error")
            return render_template("reset-password.html", username=username)
        
        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp!", "error")
            return render_template("reset-password.html", username=username)
        
        conn = get_db_connection()
        if not conn:
            flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
            return render_template("reset-password.html", username=username)
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            cursor.execute(
                "UPDATE dbo.users SET pass_word = ? WHERE user_name = ?",
                (hashed_password, username)
            )
            conn.commit()
            session.pop("reset_username", None)
            
            flash("Đặt lại mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.", "success")
            conn.close()
            return redirect(url_for("login"))
            
        except Exception as e:
            print(f"Lỗi đặt lại mật khẩu: {e}")
            try:
                conn.rollback()
            except:
                pass
            flash("Có lỗi xảy ra khi đặt lại mật khẩu. Vui lòng thử lại.", "error")
        finally:
            try:
                conn.close()
            except:
                pass
    
    return render_template("reset-password.html", username=username)

@app.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():
    username = session.get("username")
    user_service = UserService()
    is_admin = user_service.is_admin(username) if username else False
    department_service = DepartmentService()
    departments = department_service.get_all_departments()
    
    conn = get_db_connection()
    if not conn:
        flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
        return render_template("account-settings.html", 
                             username=username, 
                             email=session.get("email"), 
                             phone_number=session.get("phone_number"),
                             first_name="",
                             middle_name="",
                             last_name="",
                             department="",
                             department_key="",
                             departments=departments,
                             is_admin=is_admin)
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT u.first_name, u.middle_name, u.last_name, d.department, u.department_key
               FROM dbo.users u
               LEFT JOIN dbo.departments d ON u.department_key = d.department_key
               WHERE u.user_name = ?""",
            (username,)
        )
        user_info = cursor.fetchone()
        conn.close()
        
        first_name = user_info[0] if user_info and user_info[0] else ""
        middle_name = user_info[1] if user_info and user_info[1] else ""
        last_name = user_info[2] if user_info and user_info[2] else ""
        department = user_info[3] if user_info and user_info[3] else ""
        department_key = user_info[4] if user_info and user_info[4] else ""
    except Exception as e:
        print(f"Lỗi lấy thông tin user: {e}")
        try:
            conn.close()
        except:
            pass
        first_name = ""
        middle_name = ""
        last_name = ""
        department = ""
        department_key = ""
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        department_key = request.form.get("department_key", "").strip() if is_admin else None
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        conn = get_db_connection()
        if not conn:
            flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
            return render_template("account-settings.html", 
                                 username=username, 
                                 email=session.get("email"), 
                                 phone_number=session.get("phone_number"),
                                 first_name=first_name,
                                 middle_name=middle_name,
                                 last_name=last_name,
                                 department=department)
        
        try:
            conn.autocommit = False
            cursor = conn.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            
            if new_password:
                cursor.execute(
                    "SELECT pass_word FROM dbo.users WHERE user_name = ?",
                    (username,)
                )
                user = cursor.fetchone()
                if not user or not bcrypt.checkpw(current_password.encode("utf-8"), user[0].encode("utf-8")):
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu hiện tại không đúng!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                if len(new_password) < 8:
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu phải có ít nhất 8 ký tự!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                if not any(c.islower() for c in new_password):
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu phải có ít nhất 1 chữ cái viết thường!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                if not any(c.isupper() for c in new_password):
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu phải có ít nhất 1 chữ cái viết in hoa!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                if not any(c.isdigit() for c in new_password):
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu phải có ít nhất 1 chữ số!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                special_chars = "!@#$%^&*()_+-=[]{};:\"'\\|,.<>/?"
                if not any(c in special_chars for c in new_password):
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu phải có ít nhất 1 ký tự đặc biệt!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                if new_password != confirm_password:
                    conn.rollback()
                    conn.close()
                    flash("Mật khẩu xác nhận không khớp!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=email or session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                cursor.execute(
                    "UPDATE dbo.users SET pass_word = ? WHERE user_name = ?",
                    (hashed_password, username)
                )
            
            if phone_number:
                if phone_number.startswith("+84"):
                    phone_number = "0" + phone_number[3:]
                phone_number = "".join(filter(str.isdigit, phone_number))
                
                if not phone_number.startswith("0") or len(phone_number) != 10:
                    conn.rollback()
                    conn.close()
                    flash("Số điện thoại không hợp lệ! Phải có 10 số và bắt đầu bằng 0.", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=session.get("email"), 
                                         phone_number=session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
            
            if email:
                if "@" not in email or "." not in email.split("@")[1]:
                    conn.rollback()
                    conn.close()
                    flash("Email không hợp lệ!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
                
                cursor.execute(
                    "SELECT user_name FROM dbo.users WITH (UPDLOCK, HOLDLOCK) WHERE LOWER(email) = LOWER(?) AND user_name != ?",
                    (email, username)
                )
                if cursor.fetchone():
                    conn.rollback()
                    conn.close()
                    flash("Email đã được sử dụng bởi tài khoản khác!", "error")
                    return render_template("account-settings.html", 
                                         username=username, 
                                         email=session.get("email"), 
                                         phone_number=phone_number or session.get("phone_number"),
                                         first_name=first_name,
                                         middle_name=middle_name,
                                         last_name=last_name,
                                         department=department,
                                         department_key=department_key,
                                         departments=departments,
                                         is_admin=is_admin)
            
            update_fields = []
            update_values = []
            
            if email and email != session.get("email"):
                update_fields.append("email = ?")
                update_values.append(email)
                session["email"] = email
            
            if phone_number and phone_number != session.get("phone_number"):
                update_fields.append("phone_number = ?")
                update_values.append(phone_number)
                session["phone_number"] = phone_number
            
            if first_name is not None:
                update_fields.append("first_name = ?")
                update_values.append(first_name)
            
            if middle_name is not None:
                update_fields.append("middle_name = ?")
                update_values.append(middle_name)
            
            if last_name is not None:
                update_fields.append("last_name = ?")
                update_values.append(last_name)
            
            if update_fields:
                update_values.append(username)
                cursor.execute(
                    f"UPDATE dbo.users SET {', '.join(update_fields)} WHERE user_name = ?",
                    tuple(update_values)
                )
                conn.commit()
                
                if first_name is not None:
                    session["first_name"] = first_name
                if middle_name is not None:
                    session["middle_name"] = middle_name
                if last_name is not None:
                    session["last_name"] = last_name
            
            if is_admin and department_key is not None:
                if department_key == "":
                    cursor.execute(
                        "UPDATE dbo.users SET department_key = NULL WHERE user_name = ?",
                        (username,)
                    )
                    session["department"] = ""
                else:
                    cursor.execute(
                        "UPDATE dbo.users SET department_key = ? WHERE user_name = ?",
                        (department_key, username)
                    )
                    department_service = DepartmentService()
                    dept = department_service.get_all_departments()
                    dept_dict = {d["department_key"]: d["department"] for d in dept}
                    session["department"] = dept_dict.get(department_key, "")
                conn.commit()
            
            if update_fields or new_password or (is_admin and department_key is not None):
                flash("Cập nhật thông tin thành công!", "success")
                try:
                    conn.close()
                except:
                    pass
                return redirect(url_for("account_settings"))
            else:
                conn.commit()
                flash("Cập nhật thông tin thành công!", "success")
                try:
                    conn.close()
                except:
                    pass
                return redirect(url_for("account_settings"))
            
        except Exception as e:
            print(f"Lỗi cập nhật thông tin: {e}")
            try:
                conn.rollback()
            except:
                pass
            flash("Có lỗi xảy ra khi cập nhật thông tin. Vui lòng thử lại.", "error")
        finally:
            try:
                conn.close()
            except:
                pass
    
    return render_template("account-settings.html", 
                         username=username, 
                         email=session.get("email"), 
                         phone_number=session.get("phone_number"),
                         first_name=first_name,
                         middle_name=middle_name,
                         last_name=last_name,
                         department=department,
                         department_key=department_key,
                         departments=departments,
                         is_admin=is_admin)

@app.route("/customer-search")
@login_required
def customer_search():
    return render_template("customer-search.html")

@app.route("/role-management")
@admin_required
def role_management():
    user_service = UserService()
    role_service = RoleService()
    department_service = DepartmentService()
    users = user_service.get_all_users()
    roles = role_service.get_all_roles()
    departments = department_service.get_all_departments()
    return render_template("role-management.html", users=users, roles=roles, departments=departments)

@app.route("/api/customer/search", methods=["POST"])
@login_required
def search_customer():
    try:
        data = request.get_json()
        tax_code = data.get("tax_code", "").strip()
        
        if not tax_code:
            return jsonify({"success": False, "error": "Vui lòng nhập mã số thuế"}), 400
        
        if not tax_code.isdigit():
            return jsonify({"success": False, "error": "Mã số thuế phải là toàn các chữ số"}), 400
        
        if len(tax_code) > 11:
            return jsonify({"success": False, "error": "Mã số thuế không được vượt quá 11 ký tự"}), 400
        
        search_service = CustomerSearchService()
        result = search_service.search_by_tax_code(tax_code)
        
        if result:
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"success": False, "error": "Không tìm thấy khách hàng với mã số thuế này"}), 404
    except Exception as e:
        print(f"[search_customer] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/user/assign-role", methods=["POST"])
@admin_required
def assign_user_role():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        role_name = data.get("role_name", "").strip()
        
        if not username or not role_name:
            return jsonify({"success": False, "error": "Vui lòng điền đầy đủ thông tin"}), 400
        
        role_service = RoleService()
        role_key = role_service.get_role_key_by_name(role_name)
        
        if not role_key:
            return jsonify({"success": False, "error": "Vai trò không hợp lệ"}), 400
        
        user_service = UserService()
        success = user_service.assign_role(username, role_key)
        
        if success:
            return jsonify({"success": True, "message": "Cập nhật vai trò thành công"})
        else:
            return jsonify({"success": False, "error": "Không thể cập nhật vai trò"}), 500
    except Exception as e:
        print(f"[assign_user_role] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/user/update-info", methods=["POST"])
@admin_required
def update_user_info():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        first_name = data.get("first_name", "").strip()
        middle_name = data.get("middle_name", "").strip()
        last_name = data.get("last_name", "").strip()
        department_key = data.get("department_key", "").strip()
        role_name = data.get("role_name", "").strip()
        
        if not username:
            return jsonify({"success": False, "error": "Vui lòng điền đầy đủ thông tin"}), 400
        
        user_service = UserService()
        
        if role_name:
            role_service = RoleService()
            role_key = role_service.get_role_key_by_name(role_name)
            print(f"[update_user_info] role_name: {role_name}, role_key: {role_key}")
            if not role_key:
                return jsonify({"success": False, "error": f"Vai trò '{role_name}' không hợp lệ hoặc không tồn tại trong hệ thống"}), 400
            role_success = user_service.assign_role(username, role_key)
            print(f"[update_user_info] assign_role result: {role_success}")
            if not role_success:
                return jsonify({"success": False, "error": "Không thể cập nhật vai trò. Vui lòng kiểm tra lại thông tin."}), 500
        
        success = user_service.update_user_info(
            username=username,
            first_name=first_name if first_name else None,
            middle_name=middle_name if middle_name else None,
            last_name=last_name if last_name else None,
            department_key=department_key if department_key else None
        )
        
        if success:
            return jsonify({"success": True, "message": "Cập nhật thông tin thành công"})
        else:
            return jsonify({"success": False, "error": "Không thể cập nhật thông tin"}), 500
    except Exception as e:
        print(f"[update_user_info] Error: {e}")
        
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Có lỗi xảy ra: {str(e)}"}), 500

@app.route("/dashboard-report")
@login_required
def dashboard_report():
    return render_template("dashboard-report.html")

@app.route("/api/dashboard/total-customers")
@login_required
def api_total_customers():
    try:
        report_service = DashboardReportService()
        count = report_service.get_total_customers()
        if count is not None:
            return jsonify({"success": True, "data": count})
        else:
            return jsonify({"success": False, "error": "Không thể lấy dữ liệu"}), 500
    except Exception as e:
        print(f"[api_total_customers] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/customers-list")
@login_required
def api_customers_list():
    try:
        report_service = DashboardReportService()
        data = report_service.get_customers_list()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_customers_list] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/months-list")
@login_required
def api_months_list():
    try:
        report_service = DashboardReportService()
        data = report_service.get_months_list()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_months_list] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/customer-monthly-revenue")
@login_required
def api_customer_monthly_revenue():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        report_service = DashboardReportService()
        data = report_service.get_customer_monthly_revenue(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_customer_monthly_revenue] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/customer-container-usage")
@login_required
def api_customer_container_usage():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        report_service = DashboardReportService()
        data = report_service.get_customer_container_usage(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_customer_container_usage] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route('/api/dashboard/monthly-container-usage', methods=['GET'])
def api_monthly_container_usage():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        print(f"[api_monthly_container_usage] customer_keys: {customer_keys}, month_years: {month_years}")
        
        report_service = DashboardReportService()
        data = report_service.get_monthly_container_usage(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_monthly_container_usage] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route('/api/dashboard/monthly-container-type-usage', methods=['GET'])
def api_monthly_container_type_usage():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        print(f"[api_monthly_container_type_usage] customer_keys: {customer_keys}, month_years: {month_years}")
        
        report_service = DashboardReportService()
        data = report_service.get_monthly_container_type_usage(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_monthly_container_type_usage] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/customers-by-province")
@login_required
def api_customers_by_province():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        print(f"[api_customers_by_province] customer_keys: {customer_keys}, month_years: {month_years}")
        
        report_service = DashboardReportService()
        data = report_service.get_customers_by_province(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_customers_by_province] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/revenue-by-province")
@login_required
def api_revenue_by_province():
    try:
        customer_keys = request.args.getlist("customer_key")
        month_years = request.args.getlist("month_year")
        
        customer_keys = [k for k in customer_keys if k] if customer_keys else None
        month_years = [m for m in month_years if m] if month_years else None
        
        print(f"[api_revenue_by_province] customer_keys: {customer_keys}, month_years: {month_years}")
        
        report_service = DashboardReportService()
        data = report_service.get_revenue_by_province(customer_keys, month_years)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"[api_revenue_by_province] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/api/dashboard/data-version")
@login_required
def api_data_version():
    try:
        report_service = DashboardReportService()
        version = report_service.get_data_version()
        if version is not None:
            return jsonify({"success": True, "version": version})
        else:
            return jsonify({"success": False, "error": "Không thể lấy version"}), 500
    except Exception as e:
        print(f"[api_data_version] Error: {e}")
        return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

@app.route("/ocr")
@login_required
def ocr():
    return render_template("ocr.html")

@app.route("/ocr/process", methods=["POST"])
@login_required
def ocr_process():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Không có file được tải lên"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Chưa chọn file"})
    
    if file and file.filename.endswith('.pdf'):
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            ocr_processor = OCRProcessor()
            result = ocr_processor.process_ocr(filepath)
            
            if result.get("success"):
                data = result.get("data", {})
                tax_code = data.get("tax_code", "")
                customer_name = data.get("customer_name", "")
                customer_address = data.get("customer_address", "")
                
                if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                    customer_manager = CustomerManager()
                    customer_manager.process_and_save_customer(tax_code, customer_name, customer_address)
                
                receipt_code = data.get("transaction_code", "")
                receipt_date = data.get("receipt_date", "")
                shipment_code = data.get("lot_code", "")
                invoice_number = data.get("invoice_number", "")
                
                if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                    receipt_manager = ReceiptManager()
                    receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code)
                
                items = data.get("items", [])
                
                if items:
                    container_manager = ContainerManager()
                    container_manager.process_and_save_containers(items)
                    
                    if receipt_date and receipt_date != "-":
                        service_manager = ServiceManager()
                        service_manager.process_and_save_services(items, receipt_date)
                        
                        if receipt_code and receipt_code != "-":
                            line_manager = LineManager()
                            line_manager.process_and_save_lines(items, receipt_code, receipt_date)
                
                stats = {}
                count_service = CustomerCountService()
                customer_count = count_service.get_active_customer_count()
                if customer_count is not None:
                    stats['customer_count'] = customer_count
                
                doc_count_service = DocumentCountService()
                document_count = doc_count_service.get_document_count()
                if document_count is not None:
                    stats['document_count'] = document_count
                
                result['stats'] = stats
                return jsonify(result)
            else:
                return jsonify({"success": False, "error": result.get("error", "Không thể xử lý file PDF")})
        except Exception as e:
            print(f"Lỗi khi xử lý OCR: {e}")
            return jsonify({"success": False, "error": f"Lỗi khi xử lý OCR: {str(e)}"})
    
    return jsonify({"success": False, "error": "File không hợp lệ. Vui lòng chọn file PDF."})

@app.route("/ocr/process-multiple", methods=["POST"])
@login_required
def ocr_process_multiple():
    if 'files' not in request.files:
        return jsonify({"success": False, "error": "Không có file được tải lên"})
    
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({"success": False, "error": "Chưa chọn file"})
    
    pdf_files = [f for f in files if f.filename and f.filename.endswith('.pdf')]
    if len(pdf_files) == 0:
        return jsonify({"success": False, "error": "Không có file PDF hợp lệ"})
    
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    ocr_processor = OCRProcessor()
    results = []
    errors = []
    
    for file in pdf_files:
        filename = file.filename
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            result = ocr_processor.process_ocr(filepath)
            
            if result.get("success"):
                data = result.get("data", {})
                tax_code = data.get("tax_code", "")
                customer_name = data.get("customer_name", "")
                customer_address = data.get("customer_address", "")
                
                if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                    customer_manager = CustomerManager()
                    customer_manager.process_and_save_customer(tax_code, customer_name, customer_address)
                
                receipt_code = data.get("transaction_code", "")
                receipt_date = data.get("receipt_date", "")
                shipment_code = data.get("lot_code", "")
                invoice_number = data.get("invoice_number", "")
                
                if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                    receipt_manager = ReceiptManager()
                    receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code)
                
                items = data.get("items", [])
                
                if items:
                    container_manager = ContainerManager()
                    container_manager.process_and_save_containers(items)
                    
                    if receipt_date and receipt_date != "-":
                        service_manager = ServiceManager()
                        service_manager.process_and_save_services(items, receipt_date)
                        
                        if receipt_code and receipt_code != "-":
                            line_manager = LineManager()
                            line_manager.process_and_save_lines(items, receipt_code, receipt_date)
                
                results.append(data)
            else:
                errors.append(f"{filename}: {result.get('error', 'Lỗi không xác định')}")
        except Exception as e:
            print(f"Lỗi khi xử lý OCR cho file {filename}: {e}")
            errors.append(f"{filename}: {str(e)}")
    
    stats = {}
    count_service = CustomerCountService()
    customer_count = count_service.get_active_customer_count()
    if customer_count is not None:
        stats['customer_count'] = customer_count
    
    doc_count_service = DocumentCountService()
    document_count = doc_count_service.get_document_count()
    if document_count is not None:
        stats['document_count'] = document_count
    
    if len(results) == 0:
        return jsonify({
            "success": False,
            "error": "Không thể xử lý bất kỳ file nào. " + "; ".join(errors) if errors else "Lỗi không xác định"
        })
    
    return jsonify({
        "success": True,
        "data": results,
        "warnings": errors if errors else None,
        "stats": stats
    })

@app.route("/api/customers/count", methods=["GET"])
@login_required
def get_customer_count():
    """API endpoint để lấy số lượng khách hàng đang hoạt động"""
    try:
        count_service = CustomerCountService()
        count = count_service.get_active_customer_count()
        
        if count is None:
            return jsonify({"success": False, "error": "Không thể lấy số lượng khách hàng"}), 500
        
        return jsonify({"success": True, "count": count})
    except Exception as e:
        print(f"Lỗi khi lấy số lượng khách hàng: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/documents/count", methods=["GET"])
@login_required
def get_document_count():
    """API endpoint để lấy số lượng tài liệu đã quét"""
    try:
        count_service = DocumentCountService()
        count = count_service.get_document_count()
        
        if count is None:
            return jsonify({"success": False, "error": "Không thể lấy số lượng tài liệu"}), 500
        
        return jsonify({"success": True, "count": count})
    except Exception as e:
        print(f"Lỗi khi lấy số lượng tài liệu: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/visits/count", methods=["GET"])
@login_required
def get_visit_count():
    try:
        visit_service = VisitCountService()
        count = visit_service.get_active_visit_count()
        
        if count is None:
            return jsonify({"success": False, "error": "Không thể lấy số lượng truy cập"}), 500
        
        return jsonify({"success": True, "count": count})
    except Exception as e:
        print(f"Lỗi khi lấy số lượng truy cập: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất thành công!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
