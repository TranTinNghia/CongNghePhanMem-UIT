import jwt
import datetime
from typing import Optional, Dict
from functools import wraps
from flask import request, jsonify, session
from utils.config_helper import get_jwt_secret_key

JWT_SECRET_KEY = get_jwt_secret_key()
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def generate_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_request() -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None

def get_current_user():
    token = get_token_from_request()
    if token:
        payload = verify_token(token)
        if payload:
            return {
                "username": payload.get("username"),
                "role": payload.get("role"),
                "auth_method": "token"
            }

    if "user_id" in session:
        return {
            "username": session.get("username"),
            "role": session.get("role"),
            "auth_method": "session"
        }

    return None

def token_or_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "error": "Yêu cầu xác thực. Vui lòng cung cấp Bearer token hoặc đăng nhập."
                }), 401
            from flask import redirect, url_for
            return redirect(url_for("login"))

        request.current_user = user

        return f(*args, **kwargs)
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({
                "success": False,
                "error": "Token không được cung cấp. Vui lòng thêm header: Authorization: Bearer <token>"
            }), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Token không hợp lệ hoặc đã hết hạn"
            }), 401

        request.current_user = {
            "username": payload.get("username"),
            "role": payload.get("role"),
            "auth_method": "token"
        }

        return f(*args, **kwargs)
    return decorated_function

def admin_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({
                "success": False,
                "error": "Token không được cung cấp"
            }), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Token không hợp lệ hoặc đã hết hạn"
            }), 401

        role = payload.get("role")
        if role != "ADMIN":
            return jsonify({
                "success": False,
                "error": "Không có quyền truy cập. Yêu cầu quyền ADMIN"
            }), 403

        request.current_user = {
            "username": payload.get("username"),
            "role": role,
            "auth_method": "token"
        }

        return f(*args, **kwargs)
    return decorated_function

def editor_or_admin_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({
                "success": False,
                "error": "Token không được cung cấp"
            }), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Token không hợp lệ hoặc đã hết hạn"
            }), 401

        role = payload.get("role")
        if role not in ["ADMIN", "EDITOR"]:
            return jsonify({
                "success": False,
                "error": "Không có quyền truy cập. Yêu cầu quyền EDITOR hoặc ADMIN"
            }), 403

        request.current_user = {
            "username": payload.get("username"),
            "role": role,
            "auth_method": "token"
        }

        return f(*args, **kwargs)
    return decorated_function
