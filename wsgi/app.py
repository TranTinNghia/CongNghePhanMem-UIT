import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from functools import wraps
from flask import Flask, jsonify, redirect, url_for, session, flash
from utils.config_helper import get_flask_secret_key
from utils.auth_helper import token_or_session_required, token_required, admin_token_required, editor_or_admin_token_required
from utils.api_logger import ApiLogger
from utils.handlers import AuthHandler, HomeHandler, AccountHandler, CustomerSearchHandler, UserManagementHandler, DashboardHandler, OCRHandler, CountHandler
from features.user_management.user_service import UserService

app = Flask(
    __name__,
    template_folder=os.path.join(root_dir, "templates"),
    static_folder=os.path.join(root_dir, "static")
)
app.secret_key = get_flask_secret_key()

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 86400

@app.before_request
def before_request():
    ApiLogger.log_request()

@app.after_request
def after_request(response):
    return ApiLogger.log_response(response)

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

def editor_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        username = session.get("username")
        if not username:
            return redirect(url_for("login"))
        user_service = UserService()
        user_role = user_service.get_user_role(username)
        if user_role not in ["ADMIN", "EDITOR"]:
            return jsonify({"success": False, "error": "Bạn không có quyền thực hiện thao tác này"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    return AuthHandler.handle_login()

@app.route("/register", methods=["GET", "POST"])
def register():
    return AuthHandler.handle_register()

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    return AuthHandler.handle_forgot_password()

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    return AuthHandler.handle_reset_password()


@app.route("/home")
@login_required
def home():
    return HomeHandler.handle_home()


@app.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():
    return AccountHandler.handle_account_settings()

@app.route("/customer-search")
@login_required
def customer_search():
    return CustomerSearchHandler.handle_customer_search()

@app.route("/role-management")
@admin_required
def role_management():
    return UserManagementHandler.handle_role_management()

@app.route("/api/customer/search", methods=["POST"])
@token_required
def search_customer():
    return CustomerSearchHandler.handle_search_customer()

@app.route("/api/customer/export-csv", methods=["POST"])
@token_required
def export_customer_csv():
    return CustomerSearchHandler.handle_export_customer_csv()

@app.route("/api/user/assign-role", methods=["POST"])
@admin_token_required
def assign_user_role():
    return UserManagementHandler.handle_assign_user_role()

@app.route("/api/user/update-info", methods=["POST"])
@admin_token_required
def update_user_info():
    return UserManagementHandler.handle_update_user_info()

@app.route("/api/user/delete", methods=["POST"])
@admin_token_required
def delete_user():
    return UserManagementHandler.handle_delete_user()

@app.route("/dashboard-report")
@login_required
def dashboard_report():
    return DashboardHandler.handle_dashboard_report()

@app.route("/api/dashboard/total-customers")
@token_required
def api_total_customers():
    return DashboardHandler.handle_total_customers()

@app.route("/api/dashboard/customers-list")
@token_required
def api_customers_list():
    return DashboardHandler.handle_customers_list()

@app.route("/api/dashboard/months-list")
@token_required
def api_months_list():
    return DashboardHandler.handle_months_list()

@app.route("/api/dashboard/customer-monthly-revenue")
@token_required
def api_customer_monthly_revenue():
    return DashboardHandler.handle_customer_monthly_revenue()

@app.route("/api/dashboard/customer-container-usage")
@token_required
def api_customer_container_usage():
    return DashboardHandler.handle_customer_container_usage()

@app.route("/api/dashboard/monthly-container-usage", methods=["GET"])
@token_required
def api_monthly_container_usage():
    return DashboardHandler.handle_monthly_container_usage()

@app.route("/api/dashboard/monthly-container-type-usage", methods=["GET"])
@token_required
def api_monthly_container_type_usage():
    return DashboardHandler.handle_monthly_container_type_usage()

@app.route("/api/dashboard/customers-by-province")
@token_required
def api_customers_by_province():
    return DashboardHandler.handle_customers_by_province()

@app.route("/api/dashboard/revenue-by-province")
@token_required
def api_revenue_by_province():
    return DashboardHandler.handle_revenue_by_province()

@app.route("/api/dashboard/data-version")
@token_required
def api_data_version():
    return DashboardHandler.handle_data_version()

@app.route("/ocr")
@token_or_session_required
def ocr():
    return OCRHandler.handle_ocr()

@app.route("/ocr/process", methods=["POST"])
@token_required
def ocr_process():
    return OCRHandler.handle_ocr_process()

@app.route("/ocr/process-multiple", methods=["POST"])
@token_required
def ocr_process_multiple():
    return OCRHandler.handle_ocr_process_multiple()

@app.route("/api/customers/count", methods=["GET"])
@token_required
def get_customer_count():
    return CountHandler.handle_customer_count()

@app.route("/api/documents/count", methods=["GET"])
@token_required
def get_document_count():
    return CountHandler.handle_document_count()

@app.route("/api/visits/count", methods=["GET"])
@token_required
def get_visit_count():
    return CountHandler.handle_visit_count()

@app.route("/ocr/save", methods=["POST"])
@editor_or_admin_token_required
def ocr_save():
    return OCRHandler.handle_ocr_save()



@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất thành công!", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ssl_cert = os.path.join(root_dir, "config", "certs", "cert.pem")
    ssl_key = os.path.join(root_dir, "config", "certs", "key.pem")
    use_https = os.path.exists(ssl_cert) and os.path.exists(ssl_key)

    port = 5000
    if use_https:
        app.run(debug=True, host="0.0.0.0", port=port, ssl_context=(ssl_cert, ssl_key))
    else:
        app.run(debug=True, host="0.0.0.0", port=port)
