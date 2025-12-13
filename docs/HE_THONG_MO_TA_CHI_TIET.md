# TÀI LIỆU MÔ TẢ HỆ THỐNG ĐẦY ĐỦ

**Tên hệ thống:** Hệ thống Quản lý OCR và Báo cáo Dashboard  
**Phiên bản:** 1.0  
**Ngày tạo:** 12/12/2025  
**Tác giả:** Nhóm phát triển - Bài tập nhóm môn Công nghệ Phần mềm  
**Trường:** Đại học Công nghệ Thông tin (UIT)

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Các tính năng chính](#3-các-tính-năng-chính)
4. [Phân quyền truy cập](#4-phân-quyền-truy-cập)
5. [Cơ sở dữ liệu](#5-cơ-sở-dữ-liệu)
6. [API Endpoints](#6-api-endpoints)
7. [Luồng hoạt động](#7-luồng-hoạt-động)
8. [Bảo mật](#8-bảo-mật)
9. [Công nghệ sử dụng](#9-công-nghệ-sử-dụng)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục đích

Hệ thống Quản lý OCR và Báo cáo Dashboard là một ứng dụng web được phát triển để:

- **Xử lý OCR**: Tự động trích xuất thông tin từ tài liệu PDF sử dụng công nghệ OCR (Optical Character Recognition)
- **Quản lý dữ liệu**: Lưu trữ và quản lý thông tin khách hàng, container, dịch vụ, hóa đơn
- **Tra cứu**: Tìm kiếm và tra cứu thông tin khách hàng theo mã số thuế
- **Báo cáo**: Hiển thị thống kê và báo cáo dưới dạng dashboard với biểu đồ trực quan
- **Quản lý người dùng**: Quản lý tài khoản, phân quyền và xác thực

### 1.2 Đối tượng sử dụng

- **ADMIN**: Quản trị viên hệ thống - Toàn quyền truy cập
- **EDITOR**: Biên tập viên - Xử lý OCR, lưu dữ liệu, xem báo cáo
- **VIEWER**: Người xem - Chỉ xem thông tin và báo cáo

### 1.3 Môi trường hoạt động

- **Backend**: Python 3.x, Flask Framework
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Database**: Microsoft SQL Server
- **Web Server**: Gunicorn (Linux/WSL2), Waitress/Hypercorn (Windows)
- **OCR Engine**: Tesseract OCR

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   HTML/CSS   │  │  JavaScript  │  │  Static Files│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/HTTPS
                        │ REST API + SSR
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              WEB SERVER (Gunicorn/Waitress)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              FLASK APPLICATION (Backend)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Routes     │  │   Services   │  │  Managers    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Auth      │  │   OCR Proc   │  │  DB Helper   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ SQL Server   │ │ Tesseract   │ │ File Storage │
│  Database    │ │    OCR       │ │   (uploads)  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 Cấu trúc thư mục

```
BaiTapNhom/
├── wsgi/                    # WSGI application
│   ├── app.py              # Main Flask application
│   ├── wsgi.py             # WSGI entry point
│   └── run_app.sh          # Script khởi động server
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── login.html          # Trang đăng nhập
│   ├── dashboard.html      # Trang dashboard
│   ├── ocr.html            # Trang xử lý OCR
│   └── ...
├── static/                 # Static files (CSS, JS, images)
├── features/               # Business logic modules
│   ├── ocr/                # OCR processing
│   ├── user_management/    # User management
│   ├── customer_search/    # Customer search
│   ├── dashboard_report/   # Dashboard reports
│   └── ...
├── utils/                  # Utility modules
│   ├── auth_helper.py      # JWT authentication
│   ├── db_helper.py        # Database connection
│   ├── ocr_processor.py    # OCR processing
│   └── ...
├── config/                 # Configuration files
│   ├── config.yaml         # App configuration
│   └── database_setup.sql  # Database schema
└── docs/                   # Documentation
```

### 2.3 Mô hình Client-Server

Hệ thống sử dụng **kiến trúc client-server** với:

- **Client (Frontend)**: Browser chạy HTML/CSS/JavaScript
- **Server (Backend)**: Flask application xử lý business logic
- **Giao tiếp**: HTTP/HTTPS với REST API và Server-Side Rendering (SSR)

---

## 3. CÁC TÍNH NĂNG CHÍNH

### 3.1 Xác thực và Quản lý Người dùng

#### 3.1.1 Đăng nhập
- **Route**: `POST /login`
- **Mô tả**: Người dùng đăng nhập bằng username và password
- **Xử lý**:
  - Verify credentials trong database
  - Mã hóa password bằng bcrypt
  - Tạo session và JWT token
  - Lưu thông tin user vào session
- **Kết quả**: Redirect đến `/home` với session và JWT token

#### 3.1.2 Đăng ký
- **Route**: `POST /register`
- **Mô tả**: Người dùng mới đăng ký tài khoản
- **Đầu vào**:
  - Username (bắt buộc, unique)
  - Email (bắt buộc, unique, validate format)
  - Phone number (bắt buộc, 10 số)
  - First name, Middle name, Last name (bắt buộc)
  - Department (dropdown, bắt buộc)
  - Password (tối thiểu 8 ký tự, có chữ hoa, thường, số, ký tự đặc biệt)
  - Confirm Password
- **Xử lý**:
  - Validate tất cả thông tin
  - Kiểm tra username và email không trùng
  - Mã hóa password bằng bcrypt
  - Tự động gán role dựa trên department:
    - **ADMIN**: Phòng Công Nghệ Thông Tin
    - **EDITOR**: Tư Lệnh Và Cấp Chỉ Huy, Phòng Tài Chính - Kế Toán, Phòng Marketing, Trung Tâm Điều Độ, TCIS
    - **VIEWER**: Các phòng ban khác
- **Kết quả**: Tài khoản mới được tạo, redirect đến `/login`

#### 3.1.3 Đăng xuất
- **Route**: `GET /logout`
- **Mô tả**: Xóa session và redirect đến trang đăng nhập

#### 3.1.4 Quản lý tài khoản
- **Route**: `GET/POST /account-settings`
- **Mô tả**: Người dùng có thể cập nhật thông tin cá nhân
- **Chức năng**:
  - Cập nhật email, phone number
  - Cập nhật họ tên
  - Đổi mật khẩu (cần mật khẩu hiện tại)
  - ADMIN có thể đổi department

#### 3.1.5 Quên mật khẩu
- **Route**: `GET/POST /forgot-password`
- **Mô tả**: Người dùng có thể reset mật khẩu
- **Quy trình**: Nhập username → Reset password → Đăng nhập lại

### 3.2 Xử lý OCR

#### 3.2.1 Upload và xử lý file PDF đơn
- **Route**: `POST /ocr/process`
- **Mô tả**: Upload một file PDF để xử lý OCR
- **Yêu cầu**: 
  - File PDF (tối đa 50MB)
  - Token authentication (`@token_required`)
- **Xử lý**:
  1. Nhận file PDF từ client
  2. Lưu file vào thư mục `uploads/`
  3. Sử dụng Tesseract OCR để trích xuất text
  4. Parse thông tin từ text:
     - Mã số thuế (tax_code)
     - Tên khách hàng (customer_name)
     - Địa chỉ (customer_address)
     - Mã giao dịch (transaction_code)
     - Ngày hóa đơn (receipt_date)
     - Mã lô (lot_code)
     - Số hóa đơn (invoice_number)
     - Danh sách container (items)
  5. Trả về JSON với dữ liệu đã trích xuất
- **Kết quả**: JSON response với dữ liệu có thể chỉnh sửa

#### 3.2.2 Upload và xử lý nhiều file PDF
- **Route**: `POST /ocr/process-multiple`
- **Mô tả**: Upload nhiều file PDF cùng lúc
- **Xử lý**: Tương tự xử lý đơn, nhưng xử lý từng file và trả về danh sách kết quả
- **Kết quả**: JSON response với mảng các kết quả

#### 3.2.3 Lưu dữ liệu OCR
- **Route**: `POST /ocr/save`
- **Mô tả**: Lưu dữ liệu đã trích xuất vào database
- **Yêu cầu**: 
  - Token authentication (`@editor_or_admin_token_required`)
  - Chỉ EDITOR và ADMIN mới có quyền lưu
- **Xử lý**:
  1. Validate dữ liệu đầu vào
  2. Xử lý và lưu Customer (nếu chưa tồn tại)
  3. Xử lý và lưu Receipt (hóa đơn)
  4. Xử lý và lưu Container
  5. Xử lý và lưu Service
  6. Xử lý và lưu Line (chi tiết hóa đơn)
  7. Sử dụng SCD2 (Slowly Changing Dimension Type 2) để lưu lịch sử
- **Kết quả**: JSON response với thống kê (số khách hàng, số tài liệu)

### 3.3 Tra cứu Khách hàng

#### 3.3.1 Tìm kiếm khách hàng
- **Route**: `POST /api/customer/search`
- **Mô tả**: Tìm kiếm khách hàng theo mã số thuế
- **Yêu cầu**: Token authentication (`@token_required`)
- **Đầu vào**: `tax_code` (mã số thuế, tối đa 11 ký tự, chỉ số)
- **Xử lý**:
  - Validate mã số thuế
  - Query database tìm khách hàng
  - Lấy thông tin:
    - Thông tin cơ bản (tên, địa chỉ, tỉnh thành)
    - Doanh thu theo tháng
    - Số lượng container theo tháng
- **Kết quả**: JSON response với thông tin khách hàng và thống kê

#### 3.3.2 Xuất CSV
- **Route**: `POST /api/customer/export-csv`
- **Mô tả**: Xuất thông tin khách hàng ra file CSV
- **Yêu cầu**: Token authentication (`@token_required`)
- **Kết quả**: File CSV với BOM UTF-8 (hỗ trợ Excel)

### 3.4 Dashboard và Báo cáo

#### 3.4.1 Dashboard chính
- **Route**: `GET /home`
- **Mô tả**: Trang dashboard hiển thị thống kê nhanh
- **Thông tin hiển thị**:
  - Tổng số khách hàng (real-time)
  - Tổng số tài liệu (real-time)
  - Tổng số lượt truy cập (real-time)
  - Các card chức năng chính

#### 3.4.2 Báo cáo Dashboard
- **Route**: `GET /dashboard-report`
- **Mô tả**: Trang báo cáo chi tiết với biểu đồ
- **Tính năng**:
  - **Bộ lọc**:
    - Lọc theo khách hàng (multi-select)
    - Lọc theo tháng/năm (multi-select)
  - **Thống kê**:
    - Tổng số khách hàng
    - Doanh thu theo khách hàng và tháng (biểu đồ cột)
    - Container theo khách hàng và tháng (biểu đồ cột)
    - Sử dụng container theo khách hàng (biểu đồ tròn)
    - Phân bổ loại container (biểu đồ tròn)
    - Khách hàng theo tỉnh (biểu đồ cột)
    - Doanh thu theo tỉnh (biểu đồ cột)
  - **Tự động làm mới**: Polling để cập nhật dữ liệu mới nhất
- **API Endpoints**:
  - `GET /api/dashboard/total-customers`
  - `GET /api/dashboard/customers-list`
  - `GET /api/dashboard/months-list`
  - `GET /api/dashboard/customer-monthly-revenue`
  - `GET /api/dashboard/customer-container-usage`
  - `GET /api/dashboard/monthly-container-usage`
  - `GET /api/dashboard/monthly-container-type-usage`
  - `GET /api/dashboard/customers-by-province`
  - `GET /api/dashboard/revenue-by-province`
  - `GET /api/dashboard/data-version`

### 3.5 Quản lý Người dùng (ADMIN only)

#### 3.5.1 Quản lý vai trò
- **Route**: `GET /role-management`
- **Mô tả**: Trang quản lý người dùng và phân quyền (chỉ ADMIN)
- **Chức năng**:
  - Xem danh sách tất cả người dùng
  - Cập nhật vai trò (role) của người dùng
  - Cập nhật thông tin người dùng (họ tên, phòng ban)
  - Xóa người dùng (không thể xóa chính mình)

#### 3.5.2 API Quản lý User
- **Route**: `POST /api/user/assign-role`
  - **Mô tả**: Gán vai trò cho người dùng
  - **Yêu cầu**: `@admin_token_required`
- **Route**: `POST /api/user/update-info`
  - **Mô tả**: Cập nhật thông tin người dùng
  - **Yêu cầu**: `@admin_token_required`
- **Route**: `POST /api/user/delete`
  - **Mô tả**: Xóa người dùng
  - **Yêu cầu**: `@admin_token_required`
  - **Lưu ý**: Không thể xóa chính mình

### 3.6 Thống kê

#### 3.6.1 API Thống kê
- **Route**: `GET /api/customers/count`
  - **Mô tả**: Lấy tổng số khách hàng đang hoạt động
  - **Yêu cầu**: `@token_required`
- **Route**: `GET /api/documents/count`
  - **Mô tả**: Lấy tổng số tài liệu (receipts)
  - **Yêu cầu**: `@token_required`
- **Route**: `GET /api/visits/count`
  - **Mô tả**: Lấy tổng số lượt truy cập
  - **Yêu cầu**: `@token_required`

---

## 4. PHÂN QUYỀN TRUY CẬP

### 4.1 Các vai trò (Roles)

Hệ thống có 3 vai trò chính:

#### 4.1.1 ADMIN (Quản trị viên)
- **Quyền truy cập**: Toàn quyền
- **Chức năng**:
  - ✅ Tất cả chức năng của EDITOR và VIEWER
  - ✅ Quản lý người dùng (xem, cập nhật, xóa)
  - ✅ Gán vai trò cho người dùng
  - ✅ Cập nhật thông tin người dùng
  - ✅ Xử lý OCR và lưu dữ liệu
  - ✅ Xem tất cả báo cáo
- **Tự động gán**: Phòng Công Nghệ Thông Tin

#### 4.1.2 EDITOR (Biên tập viên)
- **Quyền truy cập**: Ghi và đọc
- **Chức năng**:
  - ✅ Tất cả chức năng của VIEWER
  - ✅ Xử lý OCR (upload, process)
  - ✅ Lưu dữ liệu OCR vào database
  - ✅ Xem tất cả báo cáo
  - ❌ Quản lý người dùng
- **Tự động gán**: 
  - Tư Lệnh Và Cấp Chỉ Huy
  - Phòng Tài Chính - Kế Toán
  - Phòng Marketing
  - Trung Tâm Điều Độ
  - Công Ty Cổ Phần Giải Pháp CNTT Tân Cảng (TCIS)

#### 4.1.3 VIEWER (Người xem)
- **Quyền truy cập**: Chỉ đọc
- **Chức năng**:
  - ✅ Xem dashboard
  - ✅ Xem báo cáo
  - ✅ Tra cứu khách hàng
  - ✅ Xuất CSV
  - ❌ Xử lý OCR
  - ❌ Lưu dữ liệu
  - ❌ Quản lý người dùng
- **Tự động gán**: Tất cả các phòng ban khác

### 4.2 Cơ chế phân quyền

#### 4.2.1 Session-based Authentication
- **Sử dụng cho**: Trang web (HTML pages)
- **Decorator**: `@login_required`, `@admin_required`
- **Kiểm tra**: `session["user_id"]` và `session["role"]`

#### 4.2.2 JWT Bearer Token Authentication
- **Sử dụng cho**: API endpoints
- **Decorators**:
  - `@token_required`: Yêu cầu token hợp lệ
  - `@admin_token_required`: Yêu cầu role = "ADMIN"
  - `@editor_or_admin_token_required`: Yêu cầu role in ["ADMIN", "EDITOR"]
  - `@token_or_session_required`: Hỗ trợ cả token và session
- **Kiểm tra**: Token trong header `Authorization: Bearer <token>`

#### 4.2.3 Bảng phân quyền chi tiết

| Chức năng | VIEWER | EDITOR | ADMIN |
|-----------|--------|--------|-------|
| Đăng nhập/Đăng ký | ✅ | ✅ | ✅ |
| Xem Dashboard | ✅ | ✅ | ✅ |
| Xem báo cáo | ✅ | ✅ | ✅ |
| Tra cứu khách hàng | ✅ | ✅ | ✅ |
| Xuất CSV | ✅ | ✅ | ✅ |
| Xử lý OCR | ❌ | ✅ | ✅ |
| Lưu dữ liệu OCR | ❌ | ✅ | ✅ |
| Quản lý người dùng | ❌ | ❌ | ✅ |
| Gán vai trò | ❌ | ❌ | ✅ |
| Xóa người dùng | ❌ | ❌ | ✅ |

### 4.3 Bảo vệ Routes

#### 4.3.1 Public Routes (Không cần đăng nhập)
- `/` - Redirect đến login hoặc home
- `/login` - Trang đăng nhập
- `/register` - Trang đăng ký
- `/forgot-password` - Quên mật khẩu
- `/reset-password` - Reset mật khẩu
- `/logout` - Đăng xuất

#### 4.3.2 Protected Routes (Cần đăng nhập)
- `/home` - Dashboard (`@login_required`)
- `/account-settings` - Cài đặt tài khoản (`@login_required`)
- `/customer-search` - Tra cứu khách hàng (`@login_required`)
- `/dashboard-report` - Báo cáo (`@login_required`)
- `/ocr` - Xử lý OCR (`@token_or_session_required`)

#### 4.3.3 Admin-only Routes
- `/role-management` - Quản lý người dùng (`@admin_required`)

---

## 5. CƠ SỞ DỮ LIỆU

### 5.1 Tổng quan

- **Hệ quản trị**: Microsoft SQL Server
- **Tên database**: `btn`
- **Kết nối**: Sử dụng `pymssql` hoặc `pyodbc`
- **Pattern**: SCD2 (Slowly Changing Dimension Type 2) cho lưu lịch sử

### 5.2 Cấu trúc Database

#### 5.2.1 Bảng Quản lý Người dùng

**`dbo.departments`** - Phòng ban
```sql
- department_key (PK, varchar(255), unique, default newid())
- department (nvarchar(50), not null)
```

**`dbo.roles`** - Vai trò
```sql
- role_key (PK, varchar(255), unique, default newid())
- role_name (nvarchar(10), not null)
  - Values: 'ADMIN', 'EDITOR', 'VIEWER'
```

**`dbo.users`** - Người dùng
```sql
- user_key (PK, varchar(255), unique, default newid())
- user_name (varchar(255), not null, unique)
- pass_word (varchar(255), not null) -- bcrypt hashed
- email (varchar(255), unique)
- phone_number (varchar(100))
- role_key (FK → roles.role_key)
- first_name (nvarchar(50))
- middle_name (nvarchar(50))
- last_name (nvarchar(50))
- department_key (FK → departments.department_key)
```

#### 5.2.2 Bảng Nghiệp vụ

**`dbo.provinces`** - Tỉnh thành (SCD2)
```sql
- province_key (PK, varchar(255), unique, default newid())
- old_province (nvarchar(100), not null) -- Tỉnh cũ
- new_province (nvarchar(100), not null) -- Tỉnh mới sau sáp nhập
- zone (nvarchar(100)) -- Vùng
- start_time (datetime2, default getdate(), not null)
- end_time (datetime2) -- NULL nếu đang active
- is_active (char(1), default 'y', not null)
```

**`dbo.customers`** - Khách hàng (SCD2)
```sql
- customer_key (PK, varchar(255), unique, default newid())
- tax_code (varchar(11), not null) -- Mã số thuế
- customer_name (nvarchar(255), not null)
- address (nvarchar(255))
- province_key (FK → provinces.province_key, not null)
- start_time (datetime2, default getdate(), not null)
- end_time (datetime2) -- NULL nếu đang active
- is_active (char(1), default 'y', not null)
```

**`dbo.containers`** - Container (SCD2)
```sql
- container_key (PK, varchar(255), unique, default newid())
- container_size (int, not null) -- Kích thước (20, 40, 45)
- container_status (char(1)) -- Trạng thái
- container_type (char(2)) -- Loại container
- start_time (datetime2, default getdate(), not null)
- end_time (datetime2) -- NULL nếu đang active
- is_active (char(1), default 'y', not null)
```

**`dbo.services`** - Dịch vụ (SCD2)
```sql
- service_key (PK, varchar(255), unique, default newid())
- service_name (nvarchar(100), not null)
- container_key (FK → containers.container_key, not null)
- from_date (datetime2)
- to_date (datetime2)
- unit_price (int, default 0)
- tax_rate (int, default 0)
- start_time (datetime2, default getdate(), not null)
- end_time (datetime2) -- NULL nếu đang active
- is_active (char(1), default 'y', not null)
```

**`dbo.receipts`** - Hóa đơn
```sql
- receipt_key (PK, varchar(255), unique, default newid())
- receipt_code (char(10), not null) -- Mã giao dịch
- receipt_date (datetime2, not null) -- Ngày hóa đơn
- shipment_code (varchar(10), not null) -- Mã lô
- invoice_number (varchar(10), not null) -- Số hóa đơn
- customer_key (FK → customers.customer_key, not null)
```

**`dbo.lines`** - Chi tiết hóa đơn
```sql
- line_key (PK, varchar(255), unique, default newid())
- receipt_key (FK → receipts.receipt_key, not null)
- container_number (varchar(11), not null) -- Số container
- service_key (FK → services.service_key, not null)
- quantity (int) -- Số lượng
- discount (int) -- Giảm giá
- amount (int) -- Thành tiền
```

### 5.3 Quan hệ giữa các bảng

```
users
  ├──→ roles (role_key)
  └──→ departments (department_key)

customers
  └──→ provinces (province_key)

receipts
  └──→ customers (customer_key)

lines
  ├──→ receipts (receipt_key)
  └──→ services (service_key)

services
  └──→ containers (container_key)
```

### 5.4 SCD2 (Slowly Changing Dimension Type 2)

Hệ thống sử dụng SCD2 để lưu lịch sử thay đổi dữ liệu:

- **Khi dữ liệu thay đổi**: 
  - Set `end_time` và `is_active = 'N'` cho record cũ
  - Tạo record mới với `start_time = now()`, `end_time = NULL`, `is_active = 'Y'`
- **Khi query**: Chỉ lấy records với `is_active = 'Y'`
- **Áp dụng cho**: `provinces`, `customers`, `containers`, `services`

### 5.5 Indexes và Constraints

- **Primary Keys**: Tất cả bảng đều có PK là `*_key` (varchar(255), unique, default newid())
- **Foreign Keys**: Tất cả relationships đều có FK constraints
- **Unique Constraints**:
  - `users.user_name` (unique)
  - `users.email` (unique, nonclustered index)
- **Indexes**: 
  - `uq_users_email` trên `users.email`

---

## 6. API ENDPOINTS

### 6.1 API Xác thực

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| POST | `/login` | Đăng nhập | Public | - |
| GET | `/logout` | Đăng xuất | Public | - |
| POST | `/register` | Đăng ký | Public | - |
| GET/POST | `/forgot-password` | Quên mật khẩu | Public | - |
| GET/POST | `/reset-password` | Reset mật khẩu | Public | - |

### 6.2 API OCR

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| POST | `/ocr/process` | Xử lý OCR file đơn | `@token_required` | All |
| POST | `/ocr/process-multiple` | Xử lý OCR nhiều file | `@token_required` | All |
| POST | `/ocr/save` | Lưu dữ liệu OCR | `@editor_or_admin_token_required` | EDITOR, ADMIN |

### 6.3 API Tra cứu

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| POST | `/api/customer/search` | Tìm kiếm khách hàng | `@token_required` | All |
| POST | `/api/customer/export-csv` | Xuất CSV | `@token_required` | All |

### 6.4 API Thống kê

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| GET | `/api/customers/count` | Tổng số khách hàng | `@token_required` | All |
| GET | `/api/documents/count` | Tổng số tài liệu | `@token_required` | All |
| GET | `/api/visits/count` | Tổng số lượt truy cập | `@token_required` | All |

### 6.5 API Báo cáo Dashboard

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| GET | `/api/dashboard/total-customers` | Tổng số khách hàng | `@token_required` | All |
| GET | `/api/dashboard/customers-list` | Danh sách khách hàng | `@token_required` | All |
| GET | `/api/dashboard/months-list` | Danh sách tháng | `@token_required` | All |
| GET | `/api/dashboard/customer-monthly-revenue` | Doanh thu theo khách hàng/tháng | `@token_required` | All |
| GET | `/api/dashboard/customer-container-usage` | Container theo khách hàng | `@token_required` | All |
| GET | `/api/dashboard/monthly-container-usage` | Container theo tháng | `@token_required` | All |
| GET | `/api/dashboard/monthly-container-type-usage` | Loại container theo tháng | `@token_required` | All |
| GET | `/api/dashboard/customers-by-province` | Khách hàng theo tỉnh | `@token_required` | All |
| GET | `/api/dashboard/revenue-by-province` | Doanh thu theo tỉnh | `@token_required` | All |
| GET | `/api/dashboard/data-version` | Version dữ liệu | `@token_required` | All |

### 6.6 API Quản lý User (ADMIN only)

| Method | Endpoint | Mô tả | Auth | Role |
|--------|----------|-------|------|------|
| POST | `/api/user/assign-role` | Gán vai trò | `@admin_token_required` | ADMIN |
| POST | `/api/user/update-info` | Cập nhật thông tin user | `@admin_token_required` | ADMIN |
| POST | `/api/user/delete` | Xóa user | `@admin_token_required` | ADMIN |

### 6.7 Format Response

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "count": 150,
  "message": "Thành công"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Mô tả lỗi"
}
```

**Status Codes:**
- `200 OK`: Thành công
- `400 Bad Request`: Dữ liệu đầu vào không hợp lệ
- `401 Unauthorized`: Chưa đăng nhập hoặc token không hợp lệ
- `403 Forbidden`: Không có quyền truy cập
- `404 Not Found`: Không tìm thấy
- `500 Internal Server Error`: Lỗi server

---

## 7. LUỒNG HOẠT ĐỘNG

### 7.1 Luồng Đăng nhập

```
1. User nhập username/password
   ↓
2. POST /login
   ↓
3. Server verify credentials (Database)
   ↓
4. Tạo session (session["user_id"], session["role"], ...)
   ↓
5. Generate JWT token (username, role, exp, iat)
   ↓
6. Lưu token vào session (session["jwt_token"])
   ↓
7. Redirect to /home
   ↓
8. Render template với JWT token trong data attribute
   ↓
9. JavaScript lấy token từ DOM
```

### 7.2 Luồng Xử lý OCR

```
1. User upload file PDF
   ↓
2. POST /ocr/process (với Bearer token)
   ↓
3. Server lưu file vào uploads/
   ↓
4. OCR Processor trích xuất text từ PDF
   ↓
5. Parse thông tin từ text:
   - Tax code, Customer name, Address
   - Transaction code, Receipt date
   - Lot code, Invoice number
   - Container items
   ↓
6. Trả về JSON với dữ liệu đã trích xuất
   ↓
7. User chỉnh sửa dữ liệu (nếu cần)
   ↓
8. POST /ocr/save (với Bearer token, role EDITOR/ADMIN)
   ↓
9. Server xử lý và lưu vào database:
   - Customer (SCD2)
   - Receipt
   - Container (SCD2)
   - Service (SCD2)
   - Line
   ↓
10. Trả về JSON với thống kê
```

### 7.3 Luồng Tra cứu Khách hàng

```
1. User nhập mã số thuế
   ↓
2. POST /api/customer/search (với Bearer token)
   ↓
3. Server validate mã số thuế
   ↓
4. Query database tìm khách hàng
   ↓
5. Lấy thông tin:
   - Thông tin cơ bản
   - Doanh thu theo tháng
   - Số lượng container theo tháng
   ↓
6. Trả về JSON với thông tin khách hàng
   ↓
7. User có thể xuất CSV (POST /api/customer/export-csv)
```

### 7.4 Luồng Xem Báo cáo

```
1. User truy cập /dashboard-report
   ↓
2. Frontend gọi các API:
   - GET /api/dashboard/customers-list
   - GET /api/dashboard/months-list
   ↓
3. User chọn bộ lọc (khách hàng, tháng)
   ↓
4. Frontend gọi API với query parameters:
   - GET /api/dashboard/customer-monthly-revenue?customer_key=...&month_year=...
   - GET /api/dashboard/customer-container-usage?...
   - ...
   ↓
5. Server query database với filters
   ↓
6. Trả về JSON với dữ liệu
   ↓
7. Frontend render biểu đồ (Chart.js)
   ↓
8. Tự động polling để cập nhật dữ liệu mới
```

---

## 8. BẢO MẬT

### 8.1 Xác thực

#### 8.1.1 Password
- **Mã hóa**: bcrypt với salt tự động
- **Yêu cầu**: 
  - Tối thiểu 8 ký tự
  - Có chữ hoa, chữ thường, số, ký tự đặc biệt
- **Storage**: Chỉ lưu hash, không lưu plain text

#### 8.1.2 Session
- **Cookie**: HttpOnly, SameSite=Lax
- **Lifetime**: 24 giờ (86400 giây)
- **Storage**: Server-side session (Flask session)

#### 8.1.3 JWT Token
- **Algorithm**: HS256 (HMAC SHA-256)
- **Secret Key**: Lấy từ config (không hardcode)
- **Expiration**: 24 giờ
- **Payload**: username, role, exp, iat
- **Transport**: Bearer token trong header `Authorization: Bearer <token>`

### 8.2 Phân quyền

- **Role-based Access Control (RBAC)**: 3 roles (ADMIN, EDITOR, VIEWER)
- **Decorators**: Kiểm tra quyền ở mọi endpoint
- **Frontend**: Ẩn/hiện UI elements dựa trên role

### 8.3 Bảo vệ dữ liệu

#### 8.3.1 SQL Injection
- **Protection**: Parameterized queries (không dùng string concatenation)
- **Example**: `cursor.execute("SELECT * FROM users WHERE user_name = ?", (username,))`

#### 8.3.2 XSS (Cross-Site Scripting)
- **Protection**: 
  - Jinja2 template auto-escape
  - Validate và sanitize user input
  - Không render user input trực tiếp

#### 8.3.3 CSRF (Cross-Site Request Forgery)
- **Protection**: SameSite cookies

#### 8.3.4 File Upload
- **Validation**: 
  - Chỉ chấp nhận file PDF
  - Giới hạn kích thước (50MB)
  - Lưu trong thư mục riêng biệt

### 8.4 HTTPS

- **Support**: SSL/TLS encryption
- **Certificate**: Self-signed certificate (development) hoặc CA-signed (production)
- **Config**: Tự động detect và sử dụng HTTPS nếu có certificate

---

## 9. CÔNG NGHỆ SỬ DỤNG

### 9.1 Backend

- **Framework**: Flask (Python)
- **WSGI Server**: Gunicorn (Linux/WSL2), Waitress/Hypercorn (Windows)
- **Database**: Microsoft SQL Server
- **ORM**: Không dùng ORM, sử dụng raw SQL với parameterized queries
- **Authentication**: JWT (PyJWT), bcrypt
- **OCR**: Tesseract OCR (pytesseract, pdfplumber, pdf2image)

### 9.2 Frontend

- **HTML/CSS**: Vanilla (không dùng framework)
- **JavaScript**: Vanilla (không dùng framework)
- **Charts**: Chart.js
- **HTTP Client**: Fetch API

### 9.3 Infrastructure

- **OS**: Linux (WSL2), Windows
- **Web Server**: Gunicorn, Waitress, Hypercorn
- **Process Manager**: Script tự động (run_app.sh, run_app.bat)

### 9.4 Development Tools

- **Version Control**: Git
- **Package Manager**: pip (requirements.txt)
- **Configuration**: YAML (config.yaml)

---

## 10. TỔNG KẾT

### 10.1 Điểm mạnh

- ✅ Kiến trúc rõ ràng, dễ bảo trì
- ✅ Phân quyền đầy đủ và chặt chẽ
- ✅ Bảo mật tốt (JWT, bcrypt, parameterized queries)
- ✅ Hỗ trợ SCD2 cho lưu lịch sử
- ✅ API RESTful đầy đủ
- ✅ Dashboard với biểu đồ trực quan
- ✅ OCR tự động hóa quy trình

### 10.2 Hạn chế

- ⚠️ Chưa có refresh token mechanism
- ⚠️ Chưa có rate limiting
- ⚠️ Chưa có token revocation (blacklist)
- ⚠️ Frontend chưa dùng framework (có thể khó scale)

### 10.3 Hướng phát triển

- 🔄 Thêm refresh token
- 🔄 Thêm rate limiting
- 🔄 Thêm token blacklist
- 🔄 Cải thiện error handling
- 🔄 Thêm logging và monitoring
- 🔄 Tối ưu performance (caching, indexing)

---

**Kết thúc tài liệu**

