# JWT và OAuth Bearer Token - Hướng dẫn Chi tiết

## MỤC LỤC

1. [Tổng quan](#1-tổng-quan)
2. [JWT (JSON Web Token)](#2-jwt-json-web-token)
3. [OAuth 2.0 Bearer Token](#3-oauth-20-bearer-token)
4. [Cách hoạt động trong dự án](#4-cách-hoạt-động-trong-dự-án)
5. [Ví dụ thực tế](#5-ví-dụ-thực-tế)
6. [Bảo mật và Best Practices](#6-bảo-mật-và-best-practices)

---

## 1. TỔNG QUAN

### 1.1 JWT là gì?

**JWT (JSON Web Token)** là một tiêu chuẩn mở (RFC 7519) định nghĩa cách truyền thông tin an toàn giữa các bên dưới dạng đối tượng JSON. Token này có thể được ký số để đảm bảo tính toàn vẹn và xác thực.

### 1.2 OAuth Bearer Token là gì?

**OAuth Bearer Token** là một loại token được sử dụng trong OAuth 2.0 framework. "Bearer" có nghĩa là "người mang" - bất kỳ ai có token này đều có thể sử dụng nó để truy cập tài nguyên được bảo vệ.

### 1.3 Mối quan hệ giữa JWT và OAuth Bearer Token

- **JWT** là một **định dạng** của token
- **OAuth Bearer Token** là một **cách sử dụng** token
- JWT có thể được sử dụng như một OAuth Bearer Token
- Bearer Token có thể là JWT hoặc các định dạng khác (opaque token)

---

## 2. JWT (JSON Web Token)

### 2.1 Cấu trúc của JWT

JWT bao gồm 3 phần, được phân cách bởi dấu chấm (`.`):

```
Header.Payload.Signature
```

#### 2.1.1 Header (Phần đầu)

Header chứa metadata về token:
- Thuật toán mã hóa (ví dụ: HS256, RS256)
- Loại token (JWT)

**Ví dụ:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Sau khi encode Base64URL:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
```

#### 2.1.2 Payload (Phần thân)

Payload chứa các claims (thông tin) về người dùng và metadata khác.

**Các loại claims:**

1. **Registered Claims** (Claims đã đăng ký):
   - `iss` (issuer): Người phát hành token
   - `sub` (subject): Chủ thể của token (thường là user ID)
   - `aud` (audience): Đối tượng nhận token
   - `exp` (expiration time): Thời gian hết hạn (Unix timestamp)
   - `nbf` (not before): Token không hợp lệ trước thời điểm này
   - `iat` (issued at): Thời điểm phát hành token

2. **Public Claims**: Có thể được định nghĩa tùy ý
3. **Private Claims**: Claims riêng tư giữa các bên

**Ví dụ Payload:**
```json
{
  "username": "admin",
  "role": "ADMIN",
  "exp": 1702281600,
  "iat": 1702195200
}
```

Sau khi encode Base64URL:
```
eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzAyMjgxNjAwLCJpYXQiOjE3MDIxOTUyMDB9
```

#### 2.1.3 Signature (Chữ ký)

Signature được tạo bằng cách:
1. Lấy Header và Payload đã encode
2. Kết hợp chúng với dấu chấm: `Header.Payload`
3. Mã hóa bằng thuật toán đã chỉ định (ví dụ: HS256) với secret key

**Công thức:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

**Ví dụ Signature:**
```
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### 2.1.4 JWT hoàn chỉnh

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzAyMjgxNjAwLCJpYXQiOjE3MDIxOTUyMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### 2.2 Quy trình hoạt động của JWT

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client    │         │   Server    │         │   Database  │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │  1. Login Request     │                       │
       │──────────────────────>│                       │
       │                       │  2. Verify Credentials│
       │                       │──────────────────────>│
       │                       │<──────────────────────│
       │                       │  3. Create JWT        │
       │  4. Return JWT        │                       │
       │<──────────────────────│                       │
       │                       │                       │
       │  5. Request with JWT  │                       │
       │──────────────────────>│                       │
       │                       │  6. Verify JWT        │
       │                       │  (No DB query!)       │
       │  7. Response          │                       │
       │<──────────────────────│                       │
```

### 2.3 Ưu điểm của JWT

1. **Stateless**: Server không cần lưu trữ session
2. **Scalable**: Dễ dàng scale horizontal
3. **Self-contained**: Token chứa tất cả thông tin cần thiết
4. **Cross-domain**: Có thể sử dụng qua nhiều domain
5. **Mobile-friendly**: Phù hợp với mobile apps

### 2.4 Nhược điểm của JWT

1. **Không thể revoke**: Token vẫn hợp lệ cho đến khi hết hạn
2. **Kích thước**: Token lớn hơn session ID
3. **Bảo mật**: Nếu secret key bị lộ, tất cả token đều bị ảnh hưởng
4. **Không thể logout ngay**: Phải đợi token hết hạn

---

## 3. OAuth 2.0 Bearer Token

### 3.1 OAuth 2.0 là gì?

OAuth 2.0 là một framework ủy quyền cho phép ứng dụng truy cập tài nguyên thay mặt người dùng mà không cần chia sẻ mật khẩu.

### 3.2 Bearer Token Authentication

Bearer Token là một loại token được sử dụng trong OAuth 2.0. Tên "Bearer" có nghĩa là "người mang" - bất kỳ ai có token đều có thể sử dụng nó.

### 3.3 Cách sử dụng Bearer Token

Bearer Token được gửi trong HTTP Header:

```
Authorization: Bearer <token>
```

**Ví dụ:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0...
```

### 3.4 OAuth 2.0 Flow

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client    │         │ Auth Server │         │   Resource  │
│             │         │             │         │   Server    │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │  1. Request Token     │                       │
       │──────────────────────>│                       │
       │                       │                       │
       │  2. Return Bearer     │                       │
       │     Token             │                       │
       │<──────────────────────│                       │
       │                       │                       │
       │  3. Request Resource  │                       │
       │     + Bearer Token     │                       │
       │──────────────────────────────────────────────>│
       │                       │                       │
       │                       │  4. Validate Token    │
       │                       │<──────────────────────│
       │                       │                       │
       │  5. Return Resource   │                       │
       │<──────────────────────────────────────────────│
```

### 3.5 Các loại Bearer Token

1. **Access Token**: Token để truy cập tài nguyên
2. **Refresh Token**: Token để làm mới access token
3. **ID Token**: Token chứa thông tin người dùng (OpenID Connect)

---

## 4. CÁCH HOẠT ĐỘNG TRONG DỰ ÁN

### 4.1 Cấu hình JWT trong dự án

Từ file `utils/auth_helper.py`:

```python
JWT_SECRET_KEY = get_jwt_secret_key()  # Secret key từ config
JWT_ALGORITHM = "HS256"                 # Thuật toán HMAC SHA-256
JWT_EXPIRATION_HOURS = 24                # Token hết hạn sau 24 giờ
```

### 4.2 Tạo JWT Token

**Hàm `generate_token()`:**

```python
def generate_token(username: str, role: str) -> str:
    payload = {
        "username": username,      # Thông tin người dùng
        "role": role,              # Vai trò (ADMIN, EDITOR, VIEWER)
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),  # Hết hạn sau 24h
        "iat": datetime.datetime.utcnow()  # Thời điểm phát hành
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token
```

**Quy trình:**
1. Tạo payload với thông tin người dùng
2. Thêm thời gian hết hạn (`exp`)
3. Thêm thời gian phát hành (`iat`)
4. Mã hóa bằng `jwt.encode()` với secret key

**Ví dụ token được tạo:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzAyMjgxNjAwLCJpYXQiOjE3MDIxOTUyMDB9.abc123...
```

### 4.3 Xác thực JWT Token

**Hàm `verify_token()`:**

```python
def verify_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token đã hết hạn
    except jwt.InvalidTokenError:
        return None  # Token không hợp lệ
```

**Quy trình:**
1. Giải mã token bằng secret key
2. Kiểm tra chữ ký
3. Kiểm tra thời gian hết hạn
4. Trả về payload nếu hợp lệ

### 4.4 Lấy Bearer Token từ Request

**Hàm `get_token_from_request()`:**

```python
def get_token_from_request() -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # Bỏ "Bearer " prefix (7 ký tự)
    return None
```

**Ví dụ HTTP Request:**
```
GET /api/customers/count HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.5 Decorator bảo vệ API

#### 4.5.1 `@token_required`

Yêu cầu Bearer token cho mọi request:

```python
@app.route("/api/customers/count", methods=["GET"])
@token_required
def get_customer_count():
    # Chỉ chạy nếu có token hợp lệ
    # request.current_user chứa thông tin người dùng
    username = request.current_user["username"]
    role = request.current_user["role"]
    # ...
```

**Flow:**
```
Client Request
    ↓
Check Authorization Header
    ↓
Extract Bearer Token
    ↓
Verify Token
    ↓
Valid? → Execute Function
Invalid? → Return 401 Unauthorized
```

#### 4.5.2 `@admin_token_required`

Yêu cầu token với role ADMIN:

```python
@app.route("/api/users", methods=["DELETE"])
@admin_token_required
def delete_user():
    # Chỉ ADMIN mới có thể truy cập
    # request.current_user["role"] phải là "ADMIN"
    # ...
```

**Flow:**
```
Client Request
    ↓
Extract & Verify Token
    ↓
Check Role in Payload
    ↓
Role == "ADMIN"? → Execute Function
Role != "ADMIN"? → Return 403 Forbidden
```

#### 4.5.3 `@token_or_session_required`

Hỗ trợ cả token và session:

```python
@app.route("/ocr")
@token_or_session_required
def ocr():
    # Có thể dùng Bearer token HOẶC session
    user = request.current_user
    # ...
```

**Flow:**
```
Client Request
    ↓
Check Bearer Token
    ↓
Token exists & valid? → Use Token
    ↓
No Token? → Check Session
    ↓
Session exists? → Use Session
    ↓
No Token & No Session? → Return 401
```

### 4.6 Quy trình đăng nhập và tạo token

Từ file `wsgi/app.py`:

```python
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    # 1. Verify credentials
    user = verify_user_credentials(username, password)
    
    if user:
        # 2. Create session
        session["user_id"] = user[0]
        session["username"] = user[0]
        session["role"] = user[7]
        
        # 3. Generate JWT token
        jwt_token = generate_token(user[0], user[7])
        
        # 4. Store token in session (for web UI)
        session["jwt_token"] = jwt_token
        
        # 5. Redirect to home
        return redirect(url_for("home"))
```

**Quy trình:**
```
User Login
    ↓
Verify Credentials (Database)
    ↓
Create Session
    ↓
Generate JWT Token
    ↓
Store Token in Session
    ↓
Return to Client
```

### 4.7 Sử dụng token trong Frontend

Từ file `templates/base.html`:

```javascript
// Lấy token từ data attribute
const jwtToken = document.body.dataset.jwtToken;

// Sử dụng trong AJAX request
fetch('/api/customers/count', {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer ' + jwtToken,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    // Xử lý response
});
```

---

## 5. VÍ DỤ THỰC TẾ

### 5.1 Ví dụ 1: Đăng nhập và nhận token

**Request:**
```http
POST /login HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

username=admin&password=secret123
```

**Response:**
- Tạo session
- Tạo JWT token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Lưu token vào session
- Redirect đến `/home`

**Token được tạo:**
```json
{
  "username": "admin",
  "role": "ADMIN",
  "exp": 1702281600,
  "iat": 1702195200
}
```

### 5.2 Ví dụ 2: Sử dụng token để gọi API

**Request:**
```http
GET /api/customers/count HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzAyMjgxNjAwLCJpYXQiOjE3MDIxOTUyMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
Content-Type: application/json
```

**Server xử lý:**
```python
@token_required  # Decorator kiểm tra token
def get_customer_count():
    # 1. Extract token từ header
    token = get_token_from_request()  # "eyJhbGciOiJIUzI1NiIs..."
    
    # 2. Verify token
    payload = verify_token(token)
    # payload = {"username": "admin", "role": "ADMIN", ...}
    
    # 3. Set current_user
    request.current_user = {
        "username": "admin",
        "role": "ADMIN"
    }
    
    # 4. Execute function
    count = get_customer_count_from_db()
    return jsonify({"success": True, "count": count})
```

**Response:**
```json
{
  "success": true,
  "count": 150
}
```

### 5.3 Ví dụ 3: Token hết hạn

**Request:**
```http
GET /api/customers/count HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (expired token)
```

**Response:**
```json
{
  "success": false,
  "error": "Token không hợp lệ hoặc đã hết hạn"
}
```
Status Code: `401 Unauthorized`

### 5.4 Ví dụ 4: Không có quyền (403 Forbidden)

**Request:**
```http
DELETE /api/users/123 HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (role: VIEWER)
```

**Response:**
```json
{
  "success": false,
  "error": "Không có quyền truy cập. Yêu cầu quyền ADMIN"
}
```
Status Code: `403 Forbidden`

### 5.5 Ví dụ 5: Decode JWT Token (Debug)

Bạn có thể decode JWT token để xem nội dung (không cần secret key):

**Sử dụng Python:**
```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIn0..."

# Decode không verify (chỉ để xem)
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
# Output: {"username": "admin", "role": "ADMIN", "exp": 1702281600, "iat": 1702195200}
```

**Sử dụng online tool:**
- https://jwt.io/
- Paste token vào để xem header, payload, và verify signature

---

## 6. BẢO MẬT VÀ BEST PRACTICES

### 6.1 Bảo mật Secret Key

**❌ KHÔNG NÊN:**
```python
JWT_SECRET_KEY = "my-secret-key"  # Quá đơn giản, dễ đoán
```

**✅ NÊN:**
```python
# Sử dụng random secret key dài
JWT_SECRET_KEY = os.urandom(32).hex()  # 64 ký tự hex
# Hoặc
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # 43 ký tự URL-safe
```

**Trong dự án:**
```python
# Từ config/config.yaml hoặc generate tự động
JWT_SECRET_KEY = get_jwt_secret_key()  # Lấy từ config, không hardcode
```

### 6.2 Thời gian hết hạn (Expiration)

**✅ Best Practice:**
- Access Token: 15 phút - 1 giờ (ngắn)
- Refresh Token: 7-30 ngày (dài)
- Trong dự án: 24 giờ (có thể điều chỉnh)

```python
JWT_EXPIRATION_HOURS = 24  # 24 giờ
```

### 6.3 HTTPS Only

**✅ Luôn sử dụng HTTPS trong production:**
- JWT token có thể bị đánh cắp qua HTTP
- Sử dụng SSL/TLS để mã hóa kết nối

```python
# Trong dự án
app.config["SESSION_COOKIE_SECURE"] = True  # Chỉ gửi cookie qua HTTPS
```

### 6.4 Validate Token mọi lúc

**✅ Luôn verify token:**
```python
def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]  # Chỉ định algorithm cụ thể
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

**⚠️ Lưu ý:** Luôn chỉ định `algorithms` để tránh lỗ hổng bảo mật.

### 6.5 Không lưu thông tin nhạy cảm trong Payload

**❌ KHÔNG NÊN:**
```python
payload = {
    "username": "admin",
    "password": "secret123",  # ❌ KHÔNG BAO GIỜ!
    "credit_card": "1234-5678-9012-3456"  # ❌ KHÔNG BAO GIỜ!
}
```

**✅ NÊN:**
```python
payload = {
    "username": "admin",
    "role": "ADMIN",
    "user_id": "123"  # ID là OK
}
```

### 6.6 Xử lý Token Revocation

**Vấn đề:** JWT là stateless, không thể revoke trước khi hết hạn.

**Giải pháp:**

1. **Token Blacklist:**
```python
# Lưu danh sách token đã revoke
blacklisted_tokens = set()

def verify_token(token: str):
    if token in blacklisted_tokens:
        return None  # Token đã bị revoke
    # ... verify như bình thường
```

2. **Short-lived tokens + Refresh tokens:**
```python
# Access token: 15 phút
access_token = generate_token(username, role, expires_in=900)

# Refresh token: 7 ngày
refresh_token = generate_refresh_token(username, role, expires_in=604800)
```

3. **Database check (hybrid):**
```python
def verify_token(token: str):
    payload = jwt.decode(token, ...)
    
    # Kiểm tra thêm trong database
    if is_token_revoked(payload["jti"]):  # jti = JWT ID
        return None
    
    return payload
```

### 6.7 CORS và Token

**✅ Cấu hình CORS đúng cách:**
```python
from flask_cors import CORS

CORS(app, 
     origins=["https://yourdomain.com"],  # Chỉ cho phép domain cụ thể
     supports_credentials=True
)
```

### 6.8 XSS Protection

**✅ Luôn escape user input:**
- JWT token không chứa executable code
- Nhưng vẫn cần escape khi hiển thị

```javascript
// ✅ NÊN: Lưu token trong memory hoặc httpOnly cookie
const token = sessionStorage.getItem('token');

// ❌ KHÔNG NÊN: Lưu trong localStorage (dễ bị XSS)
```

### 6.9 Rate Limiting

**✅ Giới hạn số lần request:**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get("Authorization", "").split()[1] if request.headers.get("Authorization") else "anonymous"
)

@app.route("/api/customers/count")
@limiter.limit("100 per hour")  # 100 requests/giờ
@token_required
def get_customer_count():
    # ...
```

### 6.10 Logging và Monitoring

**✅ Log các sự kiện quan trọng:**
```python
import logging

logger = logging.getLogger(__name__)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, ...)
        logger.info(f"Token verified for user: {payload['username']}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token attempt")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token attempt")
        return None
```

---

## 7. SO SÁNH JWT VỚI SESSION

| Tiêu chí | JWT | Session |
|----------|-----|---------|
| **Storage** | Client (localStorage/cookie) | Server (memory/DB) |
| **Stateless** | ✅ Có | ❌ Không |
| **Scalability** | ✅ Dễ scale | ⚠️ Cần shared storage |
| **Size** | ⚠️ Lớn hơn | ✅ Nhỏ (chỉ ID) |
| **Revocation** | ❌ Khó | ✅ Dễ |
| **Security** | ⚠️ Phụ thuộc secret key | ✅ Server-side |
| **Mobile** | ✅ Phù hợp | ⚠️ Khó hơn |

---

## 8. TÓM TẮT

### 8.1 JWT Flow trong dự án

```
1. User Login
   ↓
2. Server verify credentials
   ↓
3. Generate JWT token với username, role, exp, iat
   ↓
4. Return token to client
   ↓
5. Client lưu token (session hoặc localStorage)
   ↓
6. Client gửi token trong header: Authorization: Bearer <token>
   ↓
7. Server verify token (không cần query DB)
   ↓
8. Server trả về response
```

### 8.2 Key Points

1. **JWT** = Header + Payload + Signature
2. **Bearer Token** = Cách gửi token trong HTTP header
3. **Stateless** = Server không lưu session
4. **Self-contained** = Token chứa tất cả thông tin
5. **Secure** = Luôn dùng HTTPS, secret key mạnh
6. **Expiration** = Token tự động hết hạn

### 8.3 Code Examples trong dự án

**Tạo token:**
```python
token = generate_token("admin", "ADMIN")
```

**Verify token:**
```python
payload = verify_token(token)
if payload:
    username = payload["username"]
    role = payload["role"]
```

**Sử dụng decorator:**
```python
@app.route("/api/endpoint")
@token_required
def my_endpoint():
    user = request.current_user
    # ...
```

**Gửi token từ client:**
```javascript
headers: {
    'Authorization': 'Bearer ' + jwtToken
}
```

---

## TÀI LIỆU THAM KHẢO

1. **JWT Specification (RFC 7519):** https://tools.ietf.org/html/rfc7519
2. **OAuth 2.0 (RFC 6749):** https://tools.ietf.org/html/rfc6749
3. **Bearer Token Usage (RFC 6750):** https://tools.ietf.org/html/rfc6750
4. **PyJWT Documentation:** https://pyjwt.readthedocs.io/
5. **JWT.io:** https://jwt.io/ (Tool để decode/encode JWT)

---

**Kết thúc tài liệu**

