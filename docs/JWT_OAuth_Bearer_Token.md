# JWT Bearer Token - Luồng Hoạt Động Trong Dự Án

## TỔNG QUAN

Dự án sử dụng **JWT (JSON Web Token)** theo chuẩn **OAuth 2.0 Bearer Token** để xác thực các API endpoints. Token được tạo khi đăng nhập và được gửi kèm trong HTTP header `Authorization: Bearer <token>` cho mọi request API.

---

## LUỒNG HOẠT ĐỘNG ĐẦY ĐỦ

### Sơ đồ tổng quan

```
┌──────────────┐                                    ┌──────────────┐                                    ┌──────────────┐
│   Browser    │                                    │  Flask App   │                                    │   Database   │
│  (Frontend)  │                                    │  (Backend)   │                                    │              │
└──────┬───────┘                                    └──────┬───────┘                                    └──────┬───────┘
       │                                                   │                                                   │
       │                                                   │                                                   │
       │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
       │  │                        BƯỚC 1: ĐĂNG NHẬP (POST /login)                                        │ │
       │  └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
       │                                                   │                                                   │
       │  1. POST /login                                  │                                                   │
       │     Content-Type: application/x-www-form-urlencoded│                                                   │
       │     Body: username=admin&password=***            │                                                   │
       │──────────────────────────────────────────────────>│                                                   │
       │                                                   │                                                   │
       │                                                   │  2. Query Database                                │
       │                                                   │     SELECT user_name, pass_word, role_name...   │
       │                                                   │     FROM users WHERE user_name = ?               │
       │                                                   │─────────────────────────────────────────────────>│
       │                                                   │                                                   │
       │                                                   │  3. Verify Password                               │
       │                                                   │     bcrypt.checkpw(password, hashed_password)    │
       │                                                   │<─────────────────────────────────────────────────│
       │                                                   │                                                   │
       │                                                   │  4. Create Session                                │
       │                                                   │     session["user_id"] = username                │
       │                                                   │     session["username"] = username                │
       │                                                   │     session["role"] = "ADMIN"                     │
       │                                                   │                                                   │
       │                                                   │  5. Generate JWT Token                            │
       │                                                   │     generate_token(username="admin", role="ADMIN")│
       │                                                   │     → Payload: {                                  │
       │                                                   │         "username": "admin",                      │
       │                                                   │         "role": "ADMIN",                          │
       │                                                   │         "exp": 1702281600,  (24h sau)           │
       │                                                   │         "iat": 1702195200   (bây giờ)            │
       │                                                   │       }                                           │
       │                                                   │     → Sign với HS256 + Secret Key                 │
       │                                                   │     → Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...│
       │                                                   │                                                   │
       │                                                   │  6. Store Token in Session                         │
       │                                                   │     session["jwt_token"] = token                  │
       │                                                   │                                                   │
       │  7. Redirect to /home                            │                                                   │
       │     (Session cookie được set)                    │                                                   │
       │<──────────────────────────────────────────────────│                                                   │
       │                                                   │                                                   │
       │                                                   │                                                   │
       │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
       │  │                        BƯỚC 2: TRUY CẬP TRANG WEB (/home)                                      │ │
       │  └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
       │                                                   │                                                   │
       │  8. GET /home                                     │                                                   │
       │     Cookie: session=...                          │                                                   │
       │──────────────────────────────────────────────────>│                                                   │
       │                                                   │                                                   │
       │                                                   │  9. @login_required decorator                     │
       │                                                   │     Check: session["user_id"] exists?            │
       │                                                   │     ✅ Yes → Allow access                         │
       │                                                   │                                                   │
       │                                                   │  10. Render template với JWT token                │
       │                                                   │      <body data-jwt-token="eyJhbGci...">        │
       │                                                   │                                                   │
       │  11. HTML Response                                │                                                   │
       │      <body data-jwt-token="eyJhbGci...">         │                                                   │
       │<──────────────────────────────────────────────────│                                                   │
       │                                                   │                                                   │
       │  12. JavaScript lấy token                        │                                                   │
       │      const jwtToken = document.body.dataset.jwtToken│                                                   │
       │                                                   │                                                   │
       │                                                   │                                                   │
       │  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐ │
       │  │                        BƯỚC 3: GỌI API (GET /api/customers/count)                              │ │
       │  └─────────────────────────────────────────────────────────────────────────────────────────────────┘ │
       │                                                   │                                                   │
       │  13. GET /api/customers/count                     │                                                   │
       │      Authorization: Bearer eyJhbGciOiJIUzI1NiIs... │                                                   │
       │      Content-Type: application/json               │                                                   │
       │──────────────────────────────────────────────────>│                                                   │
       │                                                   │                                                   │
       │                                                   │  14. @token_required decorator                    │
       │                                                   │      a. get_token_from_request()                  │
       │                                                   │         → Extract từ header:                     │
       │                                                   │            Authorization: Bearer <token>          │
       │                                                   │         → Return: "eyJhbGciOiJIUzI1NiIs..."       │
       │                                                   │                                                   │
       │                                                   │      b. verify_token(token)                      │
       │                                                   │         → Decode token với Secret Key             │
       │                                                   │         → Verify signature (HS256)                 │
       │                                                   │         → Check expiration (exp > now)            │
       │                                                   │         → Return payload: {                       │
       │                                                   │             "username": "admin",                 │
       │                                                   │             "role": "ADMIN",                      │
       │                                                   │             "exp": 1702281600,                   │
       │                                                   │             "iat": 1702195200                    │
       │                                                   │           }                                       │
       │                                                   │                                                   │
       │                                                   │      c. Set request.current_user                 │
       │                                                   │         request.current_user = {                  │
       │                                                   │           "username": "admin",                     │
       │                                                   │           "role": "ADMIN",                        │
       │                                                   │           "auth_method": "token"                  │
       │                                                   │         }                                        │
       │                                                   │                                                   │
       │                                                   │  15. Execute API function                         │
       │                                                   │      get_customer_count()                         │
       │                                                   │      → Query database                             │
       │                                                   │─────────────────────────────────────────────────>│
       │                                                   │                                                   │
       │                                                   │  16. Database returns count                      │
       │                                                   │<─────────────────────────────────────────────────│
       │                                                   │                                                   │
       │  17. JSON Response                                │                                                   │
       │      {                                            │                                                   │
       │        "success": true,                           │                                                   │
       │        "count": 150                               │                                                   │
       │      }                                            │                                                   │
       │<──────────────────────────────────────────────────│                                                   │
       │                                                   │                                                   │
```

---

## MÔ TẢ CHI TIẾT TỪNG BƯỚC

### BƯỚC 1: ĐĂNG NHẬP (POST /login)

**1. Client gửi request đăng nhập**
- **URL**: `POST /login`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Body**: `username=admin&password=secret123`
- **Mục đích**: Xác thực người dùng và nhận JWT token

**2. Server query database**
- **File**: `wsgi/app.py` (dòng 112-120)
- **Query**: Lấy thông tin user từ database
  ```sql
  SELECT u.user_name, u.pass_word, r.role_name, ...
  FROM dbo.users u
  LEFT JOIN dbo.roles r ON u.role_key = r.role_key
  WHERE LOWER(u.user_name) = LOWER(?)
  ```

**3. Verify password**
- **File**: `wsgi/app.py` (dòng 122)
- **Method**: `bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8"))`
- **Kết quả**: ✅ Password đúng → Tiếp tục | ❌ Password sai → Trả về lỗi

**4. Tạo session**
- **File**: `wsgi/app.py` (dòng 123-132)
- **Lưu vào session**:
  - `session["user_id"]` = username
  - `session["username"]` = username
  - `session["role"]` = role từ database
  - `session["email"]`, `session["phone_number"]`, ...

**5. Generate JWT Token**
- **File**: `utils/auth_helper.py` (dòng 12-20)
- **Function**: `generate_token(username, role)`
- **Payload được tạo**:
  ```json
  {
    "username": "admin",
    "role": "ADMIN",
    "exp": 1702281600,  // UTC now + 24 hours
    "iat": 1702195200   // UTC now
  }
  ```
- **Mã hóa**: `jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")`
- **Kết quả**: Token string: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6IkFETUlOIiwiZXhwIjoxNzAyMjgxNjAwLCJpYXQiOjE3MDIxOTUyMDB9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

**6. Lưu token vào session**
- **File**: `wsgi/app.py` (dòng 139)
- **Code**: `session["jwt_token"] = jwt_token`
- **Mục đích**: Frontend có thể lấy token từ session để gửi kèm API requests

**7. Redirect về /home**
- **File**: `wsgi/app.py` (dòng 144)
- **Response**: HTTP 302 Redirect to `/home`
- **Cookie**: Session cookie được set tự động bởi Flask

---

### BƯỚC 2: TRUY CẬP TRANG WEB (/home)

**8. Client request trang home**
- **URL**: `GET /home`
- **Headers**: Cookie chứa session ID
- **Mục đích**: Hiển thị dashboard

**9. Kiểm tra đăng nhập**
- **File**: `wsgi/app.py` (dòng 45-51)
- **Decorator**: `@login_required`
- **Logic**: Kiểm tra `session["user_id"]` có tồn tại không
  - ✅ Có → Cho phép truy cập
  - ❌ Không → Redirect về `/login`

**10. Render template với JWT token**
- **File**: `wsgi/app.py` (dòng 392-402)
- **Code**: 
  ```python
  jwt_token = session.get("jwt_token")
  return render_template("dashboard.html", jwt_token=jwt_token)
  ```
- **Template**: `templates/base.html` (dòng 10)
  ```html
  <body data-jwt-token="{% if session.jwt_token %}{{ session.jwt_token }}{% endif %}">
  ```

**11. HTML Response**
- **Response**: HTML page với `data-jwt-token` attribute chứa JWT token
- **Mục đích**: JavaScript có thể lấy token từ DOM

**12. JavaScript lấy token**
- **File**: `templates/base.html` (dòng 69)
- **Code**: 
  ```javascript
  const jwtToken = document.body.dataset.jwtToken || null;
  ```
- **Kết quả**: Biến `jwtToken` chứa JWT token string

---

### BƯỚC 3: GỌI API (GET /api/customers/count)

**13. Client gửi API request**
- **URL**: `GET /api/customers/count`
- **Headers**:
  ```
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json
  ```
- **File**: `templates/base.html` (dòng 72-81)
- **Code**:
  ```javascript
  function getAuthHeaders() {
      const headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
      };
      if (jwtToken) {
          headers['Authorization'] = 'Bearer ' + jwtToken;
      }
      return headers;
  }
  ```

**14. @token_required decorator xử lý**

**14a. Extract token từ header**
- **File**: `utils/auth_helper.py` (dòng 31-35)
- **Function**: `get_token_from_request()`
- **Logic**:
  ```python
  auth_header = request.headers.get("Authorization", "")
  if auth_header.startswith("Bearer "):
      return auth_header[7:]  # Bỏ "Bearer " prefix
  return None
  ```
- **Kết quả**: Token string hoặc `None`

**14b. Verify token**
- **File**: `utils/auth_helper.py` (dòng 22-29)
- **Function**: `verify_token(token)`
- **Logic**:
  ```python
  try:
      payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
      return payload
  except jwt.ExpiredSignatureError:
      return None  # Token đã hết hạn
  except jwt.InvalidTokenError:
      return None  # Token không hợp lệ
  ```
- **Kiểm tra**:
  1. ✅ Decode token với Secret Key
  2. ✅ Verify signature (HS256)
  3. ✅ Check expiration (`exp` > current time)
  4. ✅ Return payload nếu hợp lệ
  5. ❌ Return `None` nếu không hợp lệ → Trả về 401

**14c. Set request.current_user**
- **File**: `utils/auth_helper.py` (dòng 95-99)
- **Code**:
  ```python
  request.current_user = {
      "username": payload.get("username"),
      "role": payload.get("role"),
      "auth_method": "token"
  }
  ```
- **Mục đích**: API function có thể truy cập thông tin user qua `request.current_user`

**15. Execute API function**
- **File**: `wsgi/app.py` (dòng 1386-1398)
- **Function**: `get_customer_count()`
- **Logic**:
  ```python
  @app.route("/api/customers/count", methods=["GET"])
  @token_required
  def get_customer_count():
      # request.current_user đã được set bởi decorator
      count_service = CustomerCountService()
      count = count_service.get_active_customer_count()
      return jsonify({"success": True, "count": count})
  ```
- **Lưu ý**: Không cần query database để xác thực user, vì đã verify token

**16. Database query (nếu cần)**
- API function có thể query database để lấy dữ liệu
- Không cần query lại thông tin user vì đã có trong token

**17. JSON Response**
- **Response**:
  ```json
  {
    "success": true,
    "count": 150
  }
  ```
- **Status Code**: 200 OK

---

## CÁC TRƯỜNG HỢP LỖI

### Lỗi 1: Không có token

**Request**:
```
GET /api/customers/count
(Thiếu header Authorization)
```

**Response**:
```json
{
  "success": false,
  "error": "Token không được cung cấp. Vui lòng thêm header: Authorization: Bearer <token>"
}
```
**Status Code**: `401 Unauthorized`

---

### Lỗi 2: Token hết hạn

**Request**:
```
GET /api/customers/count
Authorization: Bearer eyJhbGci... (token đã hết hạn)
```

**Response**:
```json
{
  "success": false,
  "error": "Token không hợp lệ hoặc đã hết hạn"
}
```
**Status Code**: `401 Unauthorized`

---

### Lỗi 3: Không đủ quyền (403 Forbidden)

**Request**:
```
DELETE /api/user/delete
Authorization: Bearer eyJhbGci... (role: VIEWER)
Body: {"username": "user123"}
```

**Response**:
```json
{
  "success": false,
  "error": "Không có quyền truy cập. Yêu cầu quyền ADMIN"
}
```
**Status Code**: `403 Forbidden`

**Logic**: Decorator `@admin_token_required` kiểm tra `payload.get("role") == "ADMIN"`

---

## CÁC LOẠI DECORATOR

### 1. `@token_required`
- **Mục đích**: Yêu cầu Bearer token hợp lệ
- **Sử dụng**: Tất cả API endpoints đọc dữ liệu
- **Ví dụ**: `/api/customers/count`, `/api/documents/count`

### 2. `@admin_token_required`
- **Mục đích**: Yêu cầu token với `role == "ADMIN"`
- **Sử dụng**: API quản lý user (xóa, cập nhật role)
- **Ví dụ**: `/api/user/delete`, `/api/user/assign-role`

### 3. `@editor_or_admin_token_required`
- **Mục đích**: Yêu cầu `role in ["ADMIN", "EDITOR"]`
- **Sử dụng**: API lưu dữ liệu (cần quyền ghi)
- **Ví dụ**: `/ocr/save`

### 4. `@token_or_session_required`
- **Mục đích**: Hỗ trợ cả token và session
- **Sử dụng**: Trang web UI (không chỉ API)
- **Ví dụ**: `/ocr`

---

## TÓM TẮT

1. **Đăng nhập** → Server verify credentials → Tạo JWT token → Lưu vào session
2. **Truy cập trang web** → Server render template với token → JavaScript lấy token
3. **Gọi API** → Client gửi Bearer token trong header → Decorator verify → Execute function
4. **Token chứa**: username, role, exp, iat
5. **Token được verify**: Signature, expiration, không cần query database
6. **Phân quyền**: Dựa trên `role` trong token payload

---

**Kết thúc tài liệu**
