from flask import request, session, flash, redirect, url_for, render_template, jsonify, Response
import bcrypt
import uuid
import json
import csv
import io
from datetime import datetime, timedelta
import datetime as dt_module
from utils.db_helper import get_db_connection
from utils.auth_helper import generate_token, verify_token
from features.user_management.user_service import UserService
from features.user_management.role_service import RoleService
from features.user_management.department_service import DepartmentService
from features.visits_count.count_service import VisitCountService
from features.customer_search.search_service import CustomerSearchService
from features.ocr.managers.customers import CustomerManager
from features.ocr.managers.containers import ContainerManager
from features.ocr.managers.services import ServiceManager
from features.ocr.managers.receipts import ReceiptManager
from features.ocr.managers.lines import LineManager
from utils.ocr_processor import OCRProcessor
from features.customers_count.count_service import CustomerCountService
from features.documents_count.count_service import DocumentCountService
from features.dashboard_report.report_service import DashboardReportService
import os
import traceback


class AuthHandler:
    @staticmethod
    def handle_login():
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
                print("\n" + "="*80)
                print(f"[LOGIN & JWT TOKEN GENERATION] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*80)
                print(f"\n📥 INPUT:")
                print(f"   Username: {username}")
                print(f"   Password: [REDACTED]")

                conn.autocommit = False
                cursor = conn.cursor()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")

                print(f"\n🔍 BƯỚC 1: Query database để lấy thông tin người dùng")
                print(f"   SQL Query: SELECT user_name, pass_word, email, phone_number, first_name, middle_name, last_name, role_name, department")
                print(f"   FROM dbo.users u")
                print(f"   LEFT JOIN dbo.roles r ON u.role_key = r.role_key")
                print(f"   LEFT JOIN dbo.departments d ON u.department_key = d.department_key")
                print(f"   WHERE LOWER(u.user_name) = LOWER('{username}')")

                cursor.execute(
                    """SELECT u.user_name, u.pass_word, u.email, u.phone_number, u.first_name, u.middle_name, u.last_name, r.role_name, d.department
                       FROM dbo.users u WITH (READPAST)
                       LEFT JOIN dbo.roles r ON u.role_key = r.role_key
                       LEFT JOIN dbo.departments d ON u.department_key = d.department_key
                       WHERE LOWER(u.user_name) = LOWER(?)""",
                    (username,)
                )
                user = cursor.fetchone()

                if not user:
                    print(f"   ❌ Không tìm thấy user với username: {username}")
                    print("="*80 + "\n")
                    conn.rollback()
                    flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
                    return render_template("login.html")

                print(f"   ✅ Tìm thấy user trong database")
                print(f"   Username: {user[0]}")
                print(f"   Email: {user[2]}")
                print(f"   Role: {user[7] if user[7] else 'N/A'}")
                print(f"   Department: {user[8] if user[8] else 'N/A'}")
                print(f"   Hashed Password: {user[1][:20]}...{user[1][-20:] if len(user[1]) > 40 else user[1]}")

                print(f"\n🔐 BƯỚC 2: Verify password với bcrypt")
                print(f"   Algorithm: bcrypt")
                print(f"   Input password: [REDACTED]")
                print(f"   Stored hash: {user[1][:20]}...{user[1][-20:] if len(user[1]) > 40 else user[1]}")

                password_valid = bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8"))

                if not password_valid:
                    print(f"   ❌ Password không khớp!")
                    print("="*80 + "\n")
                    conn.rollback()
                    flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
                    return render_template("login.html")

                print(f"   ✅ Password hợp lệ!")

                print(f"\n💾 BƯỚC 3: Tạo session cho người dùng")
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
                print(f"   ✅ Session đã được tạo")
                print(f"   Session ID: {session.get('session_tracking_id', 'N/A')}")
                print(f"   User ID: {session.get('user_id')}")
                print(f"   Role: {session.get('role')}")

                username_for_token = user[0]
                user_role = user[7] if user[7] else "N/A"
                print(f"\n📋 BƯỚC 4: Chuẩn bị thông tin để tạo JWT Token")
                print(f"   Username: {username_for_token}")
                print(f"   Role: {user_role}")

                print(f"\n📦 BƯỚC 5: Tạo JWT Payload")
                exp_time = dt_module.datetime.utcnow() + timedelta(hours=24)
                iat_time = dt_module.datetime.utcnow()
                payload_preview = {
                    "username": username_for_token,
                    "role": user_role,
                    "exp": exp_time.isoformat(),
                    "iat": iat_time.isoformat()
                }
                print(f"   Payload sẽ được tạo:")
                print(f"   {json.dumps(payload_preview, indent=2, ensure_ascii=False)}")
                print(f"   Expiration: {exp_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (24 giờ từ bây giờ)")
                print(f"   Issued At: {iat_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

                print(f"\n🔐 BƯỚC 6: Mã hóa JWT Token")
                print(f"   Algorithm: HS256 (theo config)")
                print(f"   Secret Key: [REDACTED - từ config JWT_SECRET_KEY]")
                jwt_token = generate_token(username_for_token, user_role)
                print(f"   ✅ Token đã được tạo thành công!")
                print(f"   Token (full): {jwt_token}")
                print(f"   Token (masked): {jwt_token[:30]}...{jwt_token[-30:]}")
                print(f"   Token length: {len(jwt_token)} characters")

                print(f"\n✅ BƯỚC 7: Verify token vừa tạo")
                verified_payload = verify_token(jwt_token)
                if verified_payload:
                    print(f"   ✅ Token hợp lệ!")
                    print(f"   Verified payload:")
                    formatted_payload = {}
                    for key, value in verified_payload.items():
                        if isinstance(value, dt_module.datetime):
                            formatted_payload[key] = value.isoformat()
                        else:
                            formatted_payload[key] = value
                    print(f"   {json.dumps(formatted_payload, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   ❌ Token không hợp lệ!")

                print(f"\n💾 BƯỚC 8: Lưu token vào session")
                session["jwt_token"] = jwt_token
                print(f"   ✅ Token đã được lưu vào session['jwt_token']")
                print(f"   Session ID: {session.get('session_tracking_id', 'N/A')}")
                print(f"   Token sẽ được sử dụng cho các API calls từ web UI")

                print("="*80 + "\n")

                conn.commit()
                conn.close()

                return redirect(url_for("home"))
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

    @staticmethod
    def get_role_by_department(department_name: str) -> str:
        if not department_name:
            return "VIEWER"

        department_name = department_name.strip()

        if department_name == "Phòng Công Nghệ Thông Tin":
            return "ADMIN"

        editor_departments = [
            "Tư Lệnh Và Cấp Chỉ Huy",
            "Phòng Tài Chính - Kế Toán",
            "Phòng Marketing",
            "Trung Tâm Điều Độ",
            "Công Ty Cổ Phần Giải Pháp CNTT Tân Cảng (TCIS)"
        ]

        if department_name in editor_departments:
            return "EDITOR"

        return "VIEWER"

    @staticmethod
    def handle_register():
        if "user_id" in session:
            return redirect(url_for("home"))

        user_service = UserService()
        role_service = RoleService()
        department_service = DepartmentService()

        departments = department_service.get_all_departments()

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            phone_number = request.form.get("phone_number", "").strip()
            first_name = request.form.get("first_name", "").strip()
            middle_name = request.form.get("middle_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            department_key = request.form.get("department_key", "").strip()

            password = request.form.get("password", "")
            confirm_password = request.form.get("confirmPassword", "")

            if not username or not email or not phone_number or not first_name or not last_name or not password or not confirm_password:
                flash("Vui lòng điền đầy đủ thông tin bắt buộc!", "error")
                return render_template("register.html", departments=departments)

            if not department_key:
                flash("Vui lòng chọn phòng ban!", "error")
                return render_template("register.html", departments=departments)

            department_name = None
            for dept in departments:
                if dept["department_key"] == department_key:
                    department_name = dept["department"]
                    break

            if not department_name:
                flash("Phòng ban không hợp lệ!", "error")
                return render_template("register.html", departments=departments)

            role_name = AuthHandler.get_role_by_department(department_name)

            role_key = role_service.get_role_key_by_name(role_name)
            if not role_key:
                flash("Không thể xác định vai trò! Vui lòng thử lại.", "error")
                return render_template("register.html", departments=departments)

            if phone_number.startswith("+84"):
                phone_number = "0" + phone_number[3:]
            phone_number = "".join(filter(str.isdigit, phone_number))

            if not phone_number.startswith("0") or len(phone_number) != 10:
                flash("Số điện thoại không hợp lệ! Phải có 10 số và bắt đầu bằng 0.", "error")
                return render_template("register.html", departments=departments)

            if "@" not in email or "." not in email.split("@")[1]:
                flash("Email không hợp lệ!", "error")
                return render_template("register.html", departments=departments)

            if len(password) < 8:
                flash("Mật khẩu phải có ít nhất 8 ký tự!", "error")
                return render_template("register.html", departments=departments)

            if not any(c.islower() for c in password):
                flash("Mật khẩu phải có ít nhất 1 chữ cái viết thường!", "error")
                return render_template("register.html", departments=departments)

            if not any(c.isupper() for c in password):
                flash("Mật khẩu phải có ít nhất 1 chữ cái viết in hoa!", "error")
                return render_template("register.html", departments=departments)

            if not any(c.isdigit() for c in password):
                flash("Mật khẩu phải có ít nhất 1 chữ số!", "error")
                return render_template("register.html", departments=departments)

            special_chars = "!@#$%^&*()_+-=[]{};:\"\"\\|,.<>/?"
            if not any(c in special_chars for c in password):
                flash("Mật khẩu phải có ít nhất 1 ký tự đặc biệt!", "error")
                return render_template("register.html", departments=departments)

            if password != confirm_password:
                flash("Mật khẩu xác nhận không khớp!", "error")
                return render_template("register.html", departments=departments)

            conn = get_db_connection()
            if not conn:
                flash("Lỗi kết nối database. Vui lòng thử lại.", "error")
                return render_template("register.html", departments=departments)

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
                    return render_template("register.html", departments=departments)

                cursor.execute(
                    "SELECT email FROM dbo.users WITH (UPDLOCK, HOLDLOCK) WHERE LOWER(email) = LOWER(?)",
                    (email,)
                )
                if cursor.fetchone():
                    conn.rollback()
                    conn.close()
                    flash("Email đã được sử dụng! Vui lòng sử dụng email khác.", "error")
                    return render_template("register.html", departments=departments)

                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                try:
                    cursor.execute(
                        "INSERT INTO dbo.users (user_name, pass_word, email, phone_number, role_key, first_name, middle_name, last_name, department_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (username, hashed_password, email, phone_number, role_key, first_name, middle_name or None, last_name, department_key)
                    )
                    conn.commit()
                    conn.close()

                    flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                    return redirect(url_for("login"))
                except Exception as ie:
                    error_type = type(ie).__name__
                    error_msg_lower = str(ie).lower()

                    if error_type == "IntegrityError" or "duplicate" in error_msg_lower or "unique constraint" in error_msg_lower or "primary key" in error_msg_lower:
                        pass
                    else:
                        raise
                    conn.rollback()
                    conn.close()
                    if "user_name" in error_msg_lower or "primary key" in error_msg_lower:
                        flash("Tên đăng nhập đã tồn tại! Vui lòng chọn tên đăng nhập khác.", "error")
                    elif "email" in error_msg_lower or "unique" in error_msg_lower:
                        flash("Email đã được sử dụng! Vui lòng sử dụng email khác.", "error")
                    else:
                        flash("Thông tin đã tồn tại! Vui lòng kiểm tra lại.", "error")
                    return render_template("register.html", departments=departments)

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

        return render_template("register.html", departments=departments)

    @staticmethod
    def handle_forgot_password():
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

    @staticmethod
    def handle_reset_password():
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

            special_chars = "!@#$%^&*()_+-=[]{};:\"\"\\|,.<>/?"
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


class HomeHandler:
    @staticmethod
    def handle_home():
        username = session.get("username")

        if username:
            visit_service = VisitCountService()
            session_tracking_id = session.get("session_tracking_id")
            if session_tracking_id:
                visit_service.record_visit(session_tracking_id)

        user_service = UserService()
        is_admin = user_service.is_admin(username) if username else False
        user_role = session.get("role") or "N/A"

        full_name = username
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
                        name_parts = [part for part in [first_name, middle_name, last_name] if part]
                        full_name = " ".join(name_parts) if name_parts else username
            except Exception as e:
                print(f"Lỗi lấy họ tên đầy đủ: {e}")
                full_name = username

        jwt_token = session.get("jwt_token")

        return render_template(
            "dashboard.html",
            username=username,
            full_name=full_name,
            email=session.get("email"),
            phone_number=session.get("phone_number"),
            is_admin=is_admin,
            user_role=user_role,
            jwt_token=jwt_token
        )


class AccountHandler:
    @staticmethod
    def handle_account_settings():
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

                    special_chars = "!@#$%^&*()_+-=[]{};:\"\"\\|,.<>/?"
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
                    update_str = ", ".join(update_fields)
                    cursor.execute(
                        f"UPDATE dbo.users SET {update_str} WHERE user_name = ?",
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


class CustomerSearchHandler:
    @staticmethod
    def handle_customer_search():
        jwt_token = session.get("jwt_token")
        return render_template("customer-search.html", jwt_token=jwt_token)

    @staticmethod
    def handle_search_customer():
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

    @staticmethod
    def handle_export_customer_csv():
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

            if not result:
                return jsonify({"success": False, "error": "Không tìm thấy khách hàng với mã số thuế này"}), 404

            output = io.StringIO()
            writer = csv.writer(output)

            output.write('\ufeff')

            header = ['Mã số thuế', 'Tên doanh nghiệp', 'Địa chỉ', 'Tỉnh thành sau sáp nhập']
            writer.writerow(header)

            data_row = [
                tax_code,
                result.get('customer_name', ''),
                result.get('address', ''),
                result.get('new_province', '')
            ]
            writer.writerow(data_row)

            writer.writerow([])

            monthly_revenue = result.get('monthly_revenue', {})
            if monthly_revenue:
                revenue_data = monthly_revenue.get('revenue', {})
                container_data = monthly_revenue.get('container_count', {})

                all_months = set(list(revenue_data.keys()) + list(container_data.keys()))
                months = sorted(all_months, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))

                if months:
                    writer.writerow(['Tháng', 'Doanh thu', 'Số lượng container'])
                    for month in months:
                        revenue = revenue_data.get(month, 0)
                        container_count = container_data.get(month, 0)
                        writer.writerow([month, revenue, container_count])

            output.seek(0)
            csv_data = output.getvalue()
            output.close()

            response = Response(
                csv_data.encode('utf-8-sig'),
                mimetype='text/csv; charset=utf-8',
                headers={
                    'Content-Disposition': f'attachment; filename=khach_hang_{tax_code}_{datetime.now().strftime("%Y%m%d")}.csv'
                }
            )

            return response

        except Exception as e:
            print(f"[export_customer_csv] Error: {e}")
            traceback.print_exc()
            return jsonify({"success": False, "error": "Có lỗi xảy ra khi xuất CSV"}), 500


class UserManagementHandler:
    @staticmethod
    def handle_role_management():
        user_service = UserService()
        role_service = RoleService()
        department_service = DepartmentService()
        users = user_service.get_all_users()
        roles = role_service.get_all_roles()
        departments = department_service.get_all_departments()
        jwt_token = session.get("jwt_token")
        return render_template("role-management.html", users=users, roles=roles, departments=departments, jwt_token=jwt_token)

    @staticmethod
    def handle_assign_user_role():
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

    @staticmethod
    def handle_update_user_info():
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
                if not role_key:
                    return jsonify({"success": False, "error": f"Vai trò \"{role_name}\" không hợp lệ hoặc không tồn tại trong hệ thống"}), 400
                role_success = user_service.assign_role(username, role_key)
                if not role_success:
                    return jsonify({"success": False, "error": "Không thể cập nhật vai trò. Vui lòng kiểm tra lại thông tin."}), 500

            success = user_service.update_user_info(
                username=username,
                first_name=first_name if first_name else None,
                middle_name=middle_name if middle_name else None,
                last_name=last_name if last_name else None,
                department_key=department_key if department_key else None,
            )

            if success:
                return jsonify({"success": True, "message": "Cập nhật thông tin thành công"})
            else:
                return jsonify({"success": False, "error": "Không thể cập nhật thông tin"}), 500
        except Exception as e:
            print(f"[update_user_info] Error: {e}")
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Có lỗi xảy ra: {str(e)}"}), 500

    @staticmethod
    def handle_delete_user():
        try:
            data = request.get_json()
            username = data.get("username", "").strip()

            if not username:
                return jsonify({"success": False, "error": "Vui lòng cung cấp tên đăng nhập"}), 400

            current_user = getattr(request, 'current_user', None)
            if current_user and current_user.get("username") == username:
                return jsonify({"success": False, "error": "Bạn không thể xóa tài khoản của chính mình"}), 400

            user_service = UserService()
            success = user_service.delete_user(username)

            if success:
                return jsonify({"success": True, "message": f"Đã xóa tài khoản {username} thành công"})
            else:
                return jsonify({"success": False, "error": "Không thể xóa tài khoản. Vui lòng kiểm tra lại."}), 500
        except Exception as e:
            print(f"[delete_user] Error: {e}")
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Có lỗi xảy ra: {str(e)}"}), 500


class DashboardHandler:
    @staticmethod
    def handle_dashboard_report():
        jwt_token = session.get("jwt_token")
        return render_template("dashboard-report.html", jwt_token=jwt_token)

    @staticmethod
    def handle_total_customers():
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

    @staticmethod
    def handle_customers_list():
        try:
            report_service = DashboardReportService()
            data = report_service.get_customers_list()
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_customers_list] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_months_list():
        try:
            report_service = DashboardReportService()
            data = report_service.get_months_list()
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_months_list] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_customer_monthly_revenue():
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

    @staticmethod
    def handle_customer_container_usage():
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

    @staticmethod
    def handle_monthly_container_usage():
        try:
            customer_keys = request.args.getlist("customer_key")
            month_years = request.args.getlist("month_year")

            customer_keys = [k for k in customer_keys if k] if customer_keys else None
            month_years = [m for m in month_years if m] if month_years else None

            report_service = DashboardReportService()
            data = report_service.get_monthly_container_usage(customer_keys, month_years)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_monthly_container_usage] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_monthly_container_type_usage():
        try:
            customer_keys = request.args.getlist("customer_key")
            month_years = request.args.getlist("month_year")

            customer_keys = [k for k in customer_keys if k] if customer_keys else None
            month_years = [m for m in month_years if m] if month_years else None

            report_service = DashboardReportService()
            data = report_service.get_monthly_container_type_usage(customer_keys, month_years)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_monthly_container_type_usage] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_customers_by_province():
        try:
            customer_keys = request.args.getlist("customer_key")
            month_years = request.args.getlist("month_year")

            customer_keys = [k for k in customer_keys if k] if customer_keys else None
            month_years = [m for m in month_years if m] if month_years else None

            report_service = DashboardReportService()
            data = report_service.get_customers_by_province(customer_keys, month_years)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_customers_by_province] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_revenue_by_province():
        try:
            customer_keys = request.args.getlist("customer_key")
            month_years = request.args.getlist("month_year")

            customer_keys = [k for k in customer_keys if k] if customer_keys else None
            month_years = [m for m in month_years if m] if month_years else None

            report_service = DashboardReportService()
            data = report_service.get_revenue_by_province(customer_keys, month_years)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            print(f"[api_revenue_by_province] Error: {e}")
            return jsonify({"success": False, "error": "Có lỗi xảy ra"}), 500

    @staticmethod
    def handle_data_version():
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


class OCRHandler:
    @staticmethod
    def handle_ocr():
        try:
            user = getattr(request, 'current_user', None)

            if user and user.get("auth_method") == "token":
                username = user.get("username")
                user_role = user.get("role")
            else:
                username = session.get("username")
                if not username:
                    flash("Vui lòng đăng nhập để truy cập trang này", "error")
                    return redirect(url_for("login"))
                user_service = UserService()
                user_role = user_service.get_user_role(username) if username else None

            can_edit = user_role in ["ADMIN", "EDITOR"] if user_role else False
            return render_template("ocr.html", can_edit=can_edit, user_role=user_role or "N/A")
        except Exception as e:
            print(f"[ocr route] Error: {e}")
            traceback.print_exc()
            flash("Có lỗi xảy ra khi tải trang. Vui lòng thử lại.", "error")
            return redirect(url_for("home"))

    @staticmethod
    def handle_ocr_process():
        if "file" not in request.files:
            return jsonify({"success": False, "error": "Không có file được tải lên"})

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "Chưa chọn file"})

        if file and file.filename.endswith(".pdf"):
            upload_folder = "uploads"
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filename = file.filename
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            try:
                ocr_processor = OCRProcessor()
                result = ocr_processor.process_ocr(filepath)

                if result.get("success"):
                    return jsonify(result)
                else:
                    return jsonify({"success": False, "error": result.get("error", "Không thể xử lý file PDF")})
            except Exception as e:
                print(f"Lỗi khi xử lý OCR: {e}")
                return jsonify({"success": False, "error": f"Lỗi khi xử lý OCR: {str(e)}"})

        return jsonify({"success": False, "error": "File không hợp lệ. Vui lòng chọn file PDF."})

    @staticmethod
    def handle_ocr_process_multiple():
        if "files" not in request.files:
            return jsonify({"success": False, "error": "Không có file được tải lên"})

        files = request.files.getlist("files")
        if not files or len(files) == 0:
            return jsonify({"success": False, "error": "Chưa chọn file"})

        pdf_files = [f for f in files if f.filename and f.filename.endswith(".pdf")]
        if len(pdf_files) == 0:
            return jsonify({"success": False, "error": "Không có file PDF hợp lệ"})

        upload_folder = "uploads"
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
                    results.append(result.get("data", {}))
                else:
                    error_msg = result.get("error", "Lỗi không xác định")
                    errors.append(f"{filename}: {error_msg}")
            except Exception as e:
                print(f"Lỗi khi xử lý OCR cho file {filename}: {e}")
                errors.append(f"{filename}: {str(e)}")

        if len(results) == 0:
            return jsonify({
                "success": False,
                "error": "Không thể xử lý bất kỳ file nào. " + "; ".join(errors) if errors else "Lỗi không xác định"
            })

        return jsonify({
            "success": True,
            "data": results,
            "warnings": errors if errors else None
        })

    @staticmethod
    def handle_ocr_save():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "Không có dữ liệu"}), 400

            is_multiple = data.get("is_multiple", False)

            errors = []
            if is_multiple:
                results = data.get("data", [])
                if not results:
                    return jsonify({"success": False, "error": "Không có dữ liệu để lưu"}), 400

                for result in results:
                    tax_code = result.get("tax_code", "")
                    customer_name = result.get("customer_name", "")
                    customer_address = result.get("customer_address", "")

                    if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                        customer_manager = CustomerManager()
                        if not customer_manager.process_and_save_customer(tax_code, customer_name, customer_address):
                            errors.append(f"Không thể lưu customer: {customer_name}")

                    receipt_code = result.get("transaction_code", "")
                    receipt_date = result.get("receipt_date", "")
                    shipment_code = result.get("lot_code", "")
                    invoice_number = result.get("invoice_number", "")

                    if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                        receipt_manager = ReceiptManager()
                        if not receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code):
                            errors.append(f"Không thể lưu receipt: {receipt_code}")

                    items = result.get("items", [])

                    if items:

                        if not isinstance(items, list):
                            items = list(items) if items else []

                        container_manager = ContainerManager()
                        containers_saved = container_manager.process_and_save_containers(items)
                        if containers_saved == 0:
                            errors.append("Không thể lưu containers")

                        if receipt_date and receipt_date != "-":
                            service_manager = ServiceManager()
                            services_saved = service_manager.process_and_save_services(items, receipt_date)
                            if services_saved == 0:
                                errors.append("Không thể lưu services")

                            if receipt_code and receipt_code != "-":
                                line_manager = LineManager()
                                lines_saved = line_manager.process_and_save_lines(items, receipt_code, receipt_date)
                                if lines_saved == 0:
                                    errors.append("Không thể lưu lines")
            else:
                tax_code = data.get("tax_code", "")
                customer_name = data.get("customer_name", "")
                customer_address = data.get("customer_address", "")

                errors = []
                if tax_code and tax_code != "-" and customer_name and customer_name != "-" and customer_address and customer_address != "-":
                    customer_manager = CustomerManager()
                    if not customer_manager.process_and_save_customer(tax_code, customer_name, customer_address):
                        errors.append(f"Không thể lưu customer: {customer_name}")

                receipt_code = data.get("transaction_code", "")
                receipt_date = data.get("receipt_date", "")
                shipment_code = data.get("lot_code", "")
                invoice_number = data.get("invoice_number", "")

                if receipt_code and receipt_code != "-" and receipt_date and receipt_date != "-" and shipment_code and shipment_code != "-" and invoice_number and invoice_number != "-" and tax_code and tax_code != "-":
                    receipt_manager = ReceiptManager()
                    if not receipt_manager.process_and_save_receipt(receipt_code, receipt_date, shipment_code, invoice_number, tax_code):
                        errors.append(f"Không thể lưu receipt: {receipt_code}")

                items = data.get("items", [])

                if items:

                    if not isinstance(items, list):
                        items = list(items) if items else []

                    container_manager = ContainerManager()
                    containers_saved = container_manager.process_and_save_containers(items)
                    if containers_saved == 0:
                        errors.append("Không thể lưu containers")

                    if receipt_date and receipt_date != "-":
                        service_manager = ServiceManager()
                        services_saved = service_manager.process_and_save_services(items, receipt_date)
                        if services_saved == 0:
                            errors.append("Không thể lưu services")

                        if receipt_code and receipt_code != "-":
                            line_manager = LineManager()
                            lines_saved = line_manager.process_and_save_lines(items, receipt_code, receipt_date)
                            if lines_saved == 0:
                                errors.append("Không thể lưu lines")

            stats = {}
            count_service = CustomerCountService()
            customer_count = count_service.get_active_customer_count()
            if customer_count is not None:
                stats["customer_count"] = customer_count

            doc_count_service = DocumentCountService()
            document_count = doc_count_service.get_document_count()
            if document_count is not None:
                stats["document_count"] = document_count

            if errors:
                return jsonify({
                    "success": False,
                    "error": "Có lỗi khi lưu dữ liệu: " + "; ".join(errors),
                    "errors": errors
                }), 500

            response_data = {
                "success": True,
                "message": "Lưu dữ liệu thành công"
            }

            response_data["stats"] = stats

            return jsonify(response_data)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu OCR: {e}")
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Lỗi khi lưu dữ liệu: {str(e)}"}), 500


class CountHandler:
    @staticmethod
    def handle_customer_count():
        try:
            count_service = CustomerCountService()
            count = count_service.get_active_customer_count()

            if count is None:
                return jsonify({"success": False, "error": "Không thể lấy số lượng khách hàng"}), 500

            return jsonify({"success": True, "count": count})
        except Exception as e:
            print(f"Lỗi khi lấy số lượng khách hàng: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def handle_document_count():
        try:
            count_service = DocumentCountService()
            count = count_service.get_document_count()

            if count is None:
                return jsonify({"success": False, "error": "Không thể lấy số lượng tài liệu"}), 500

            return jsonify({"success": True, "count": count})
        except Exception as e:
            print(f"Lỗi khi lấy số lượng tài liệu: {e}")
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def handle_visit_count():
        try:
            visit_service = VisitCountService()
            count = visit_service.get_active_visit_count()

            if count is None:
                return jsonify({"success": False, "error": "Không thể lấy số lượng truy cập"}), 500

            return jsonify({"success": True, "count": count})
        except Exception as e:
            print(f"Lỗi khi lấy số lượng truy cập: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
