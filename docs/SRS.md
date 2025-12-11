# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## Tài liệu Đặc tả Yêu cầu Phần mềm

**Tên dự án:** Hệ thống Quản lý OCR và Báo cáo Dashboard  
**Phiên bản:** 1.0  
**Ngày tạo:** 11/12/2025  
**Tác giả:** Nhóm phát triển - Bài tập nhóm môn Công nghệ Phần mềm  
**Trường:** Đại học Công nghệ Thông tin (UIT)

---

## MỤC LỤC

1. [Giới thiệu](#1-giới-thiệu)
2. [Mô tả tổng quan](#2-mô-tả-tổng-quan)
3. [Yêu cầu chức năng](#3-yêu-cầu-chức-năng)
4. [Yêu cầu giao diện bên ngoài](#4-yêu-cầu-giao-diện-bên-ngoài)
5. [Thuộc tính hệ thống](#5-thuộc-tính-hệ-thống)
6. [Các yêu cầu khác](#6-các-yêu-cầu-khác)

---

## 1. GIỚI THIỆU

### 1.1 Mục đích

Tài liệu này mô tả đặc tả yêu cầu phần mềm (SRS) cho hệ thống Quản lý OCR và Báo cáo Dashboard. Tài liệu này được sử dụng để:
- Xác định các yêu cầu chức năng và phi chức năng của hệ thống
- Làm cơ sở cho việc thiết kế và phát triển hệ thống
- Làm tài liệu tham khảo cho các bên liên quan

### 1.2 Phạm vi

Hệ thống Quản lý OCR và Báo cáo Dashboard là một ứng dụng web được phát triển để:
- Xử lý và trích xuất thông tin từ tài liệu PDF sử dụng công nghệ OCR (Optical Character Recognition)
- Quản lý thông tin khách hàng, container, dịch vụ và hóa đơn
- Cung cấp chức năng tra cứu và tìm kiếm thông tin
- Hiển thị báo cáo và thống kê dữ liệu dưới dạng dashboard
- Quản lý người dùng và phân quyền truy cập

### 1.3 Định nghĩa, từ viết tắt và thuật ngữ

- **OCR**: Optical Character Recognition - Nhận dạng ký tự quang học
- **PDF**: Portable Document Format - Định dạng tài liệu di động
- **API**: Application Programming Interface - Giao diện lập trình ứng dụng
- **WSGI**: Web Server Gateway Interface - Giao diện cổng web server
- **ASGI**: Asynchronous Server Gateway Interface - Giao diện cổng server bất đồng bộ
- **SCD2**: Slowly Changing Dimension Type 2 - Kỹ thuật lưu trữ lịch sử thay đổi dữ liệu
- **JWT**: JSON Web Token - Token xác thực dạng JSON

### 1.4 Tài liệu tham khảo

- IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications
- Flask Framework Documentation: https://flask.palletsprojects.com/
- Tesseract OCR Documentation: https://github.com/tesseract-ocr/tesseract

### 1.5 Tổng quan

Tài liệu này được tổ chức thành 6 phần chính:
- Phần 1: Giới thiệu và mục đích của tài liệu
- Phần 2: Mô tả tổng quan về hệ thống
- Phần 3: Yêu cầu chức năng chi tiết
- Phần 4: Yêu cầu giao diện bên ngoài
- Phần 5: Thuộc tính hệ thống (hiệu năng, bảo mật, v.v.)
- Phần 6: Các yêu cầu khác

---

## 2. MÔ TẢ TỔNG QUAN

### 2.1 Quan điểm sản phẩm

Hệ thống Quản lý OCR và Báo cáo Dashboard là một ứng dụng web độc lập, được thiết kế để tự động hóa quy trình xử lý tài liệu PDF, trích xuất thông tin và quản lý dữ liệu liên quan đến khách hàng, container, dịch vụ và hóa đơn.

### 2.2 Chức năng sản phẩm

Hệ thống cung cấp các chức năng chính sau:

1. **Xử lý OCR**: Trích xuất thông tin từ file PDF bằng công nghệ OCR
2. **Quản lý dữ liệu**: Lưu trữ và quản lý thông tin khách hàng, container, dịch vụ, hóa đơn
3. **Tra cứu**: Tìm kiếm và tra cứu thông tin khách hàng
4. **Báo cáo**: Hiển thị thống kê và báo cáo dưới dạng dashboard với biểu đồ
5. **Quản lý người dùng**: Quản lý tài khoản, phân quyền và xác thực

### 2.3 Đặc điểm người dùng

Hệ thống hỗ trợ 3 loại người dùng với các quyền khác nhau:

1. **ADMIN (Quản trị viên)**
   - Toàn quyền truy cập và quản lý hệ thống
   - Quản lý người dùng và phân quyền
   - Xử lý OCR và lưu dữ liệu
   - Xem báo cáo và thống kê

2. **EDITOR (Biên tập viên)**
   - Xử lý OCR và lưu dữ liệu
   - Tra cứu thông tin
   - Xem báo cáo và thống kê
   - Không có quyền quản lý người dùng

3. **VIEWER (Người xem)**
   - Chỉ xem thông tin và báo cáo
   - Tra cứu thông tin
   - Không có quyền xử lý OCR hoặc chỉnh sửa dữ liệu

### 2.4 Ràng buộc

#### 2.4.1 Ràng buộc phần cứng
- Server: Tối thiểu 2GB RAM, 10GB dung lượng lưu trữ
- Client: Trình duyệt web hiện đại (Chrome, Firefox, Edge, Safari)

#### 2.4.2 Ràng buộc phần mềm
- Hệ điều hành server: Linux (WSL2), Windows Server
- Python: Phiên bản 3.10 trở lên
- Database: Microsoft SQL Server
- Web Server: Gunicorn (Linux), Waitress/Hypercorn (Windows)

#### 2.4.3 Ràng buộc giao tiếp
- Giao thức: HTTP/HTTPS
- Port mặc định: 5000
- Hỗ trợ SSL/TLS cho kết nối bảo mật

#### 2.4.4 Ràng buộc bộ nhớ
- Dung lượng upload file: Tối đa 50MB mỗi file PDF
- Dung lượng lưu trữ: Phụ thuộc vào cấu hình database

### 2.5 Giả định và phụ thuộc

- Người dùng có kết nối internet ổn định
- Database server luôn sẵn sàng và có thể truy cập
- File PDF được upload có định dạng hợp lệ
- Tesseract OCR engine đã được cài đặt trên server

---

## 3. YÊU CẦU CHỨC NĂNG

### 3.1 Xác thực và Phân quyền

#### 3.1.1 Đăng nhập
- **Mô tả**: Người dùng có thể đăng nhập vào hệ thống bằng username và password
- **Đầu vào**: Username, Password
- **Đầu ra**: Session được tạo, chuyển hướng đến trang dashboard
- **Xử lý**: 
  - Kiểm tra username và password trong database
  - Mã hóa password bằng bcrypt
  - Tạo session và JWT token
  - Lưu thông tin người dùng vào session

#### 3.1.2 Đăng ký
- **Mô tả**: Người dùng mới có thể đăng ký tài khoản
- **Đầu vào**: Username, Email, Phone, First Name, Last Name, Department, Password, Confirm Password
- **Đầu ra**: Tài khoản mới được tạo, tự động gán role dựa trên phòng ban
- **Xử lý**:
  - Validate thông tin đầu vào
  - Kiểm tra username và email không trùng lặp
  - Validate password (tối thiểu 8 ký tự, có chữ hoa, chữ thường, số, ký tự đặc biệt)
  - Mã hóa password và lưu vào database
  - Tự động gán role: ADMIN cho "Phòng Công Nghệ Thông Tin", EDITOR cho các phòng khác

#### 3.1.3 Đăng xuất
- **Mô tả**: Người dùng có thể đăng xuất khỏi hệ thống
- **Xử lý**: Xóa session và chuyển hướng đến trang đăng nhập

#### 3.1.4 Phân quyền
- **Mô tả**: Hệ thống kiểm tra quyền truy cập dựa trên role của người dùng
- **Quyền ADMIN**: Toàn quyền truy cập
- **Quyền EDITOR**: Xử lý OCR, lưu dữ liệu, xem báo cáo
- **Quyền VIEWER**: Chỉ xem thông tin và báo cáo

### 3.2 Xử lý OCR

#### 3.2.1 Upload và xử lý file PDF đơn
- **Mô tả**: Người dùng có thể upload một file PDF để xử lý OCR
- **Đầu vào**: File PDF (tối đa 50MB)
- **Đầu ra**: Dữ liệu được trích xuất từ PDF
- **Xử lý**:
  - Nhận file PDF từ client
  - Lưu file vào thư mục uploads
  - Trích xuất text từ PDF (sử dụng pdfplumber hoặc OCR)
  - Phân tích và trích xuất các thông tin:
    - Mã lô hàng (Lot Code)
    - Mã giao dịch (Transaction Code)
    - Ngày hóa đơn (Receipt Date)
    - Số hóa đơn (Invoice Number)
    - Mã số thuế (Tax Code)
    - Tên khách hàng (Customer Name)
    - Địa chỉ khách hàng (Customer Address)
    - Danh sách items (container, dịch vụ)

#### 3.2.2 Upload và xử lý nhiều file PDF
- **Mô tả**: Người dùng có thể upload nhiều file PDF cùng lúc
- **Đầu vào**: Nhiều file PDF
- **Đầu ra**: Danh sách dữ liệu được trích xuất từ các file
- **Xử lý**: Xử lý từng file tuần tự hoặc song song

#### 3.2.3 Trích xuất thông tin container
- **Mô tả**: Từ text đã trích xuất, hệ thống phân tích và trích xuất thông tin container
- **Thông tin trích xuất**:
  - Kích thước container (20ft, 40ft, 45ft)
  - Trạng thái container (Empty, Full, v.v.)
  - Loại container (Dry, Reefer, v.v.)
  - Số lượng
  - Đơn giá
  - Thuế suất

#### 3.2.4 Trích xuất thông tin dịch vụ
- **Mô tả**: Phân tích và trích xuất thông tin dịch vụ từ text
- **Thông tin trích xuất**:
  - Tên dịch vụ
  - Đơn giá
  - Thuế suất
  - Ngày dịch vụ

### 3.3 Quản lý Dữ liệu

#### 3.3.1 Lưu thông tin khách hàng
- **Mô tả**: Lưu thông tin khách hàng vào database với kỹ thuật SCD2
- **Dữ liệu lưu**:
  - Mã số thuế (Tax Code) - Primary Key
  - Tên khách hàng
  - Địa chỉ
  - Tỉnh/Thành phố
  - Trạng thái (Active/Inactive)
  - Ngày bắt đầu hiệu lực
  - Ngày kết thúc hiệu lực

#### 3.3.2 Lưu thông tin container
- **Mô tả**: Lưu thông tin container vào database
- **Dữ liệu lưu**:
  - Container Key (tự động tạo)
  - Kích thước container
  - Trạng thái container
  - Loại container
  - Số lượng

#### 3.3.3 Lưu thông tin dịch vụ
- **Mô tả**: Lưu thông tin dịch vụ vào database
- **Dữ liệu lưu**:
  - Service Key
  - Container Key (liên kết)
  - Tên dịch vụ
  - Đơn giá
  - Thuế suất
  - Ngày dịch vụ

#### 3.3.4 Lưu thông tin hóa đơn
- **Mô tả**: Lưu thông tin hóa đơn vào database
- **Dữ liệu lưu**:
  - Receipt Code (Transaction Code)
  - Receipt Date
  - Shipment Code (Lot Code)
  - Invoice Number
  - Tax Code (liên kết với khách hàng)

#### 3.3.5 Lưu thông tin dòng hóa đơn (Lines)
- **Mô tả**: Lưu chi tiết các dòng trong hóa đơn
- **Dữ liệu lưu**:
  - Line Key
  - Receipt Code
  - Receipt Date
  - Item information
  - Container information

### 3.4 Tra cứu Thông tin

#### 3.4.1 Tìm kiếm khách hàng
- **Mô tả**: Người dùng có thể tìm kiếm khách hàng theo nhiều tiêu chí
- **Tiêu chí tìm kiếm**:
  - Mã số thuế
  - Tên khách hàng
  - Địa chỉ
  - Tỉnh/Thành phố
- **Đầu ra**: Danh sách khách hàng khớp với tiêu chí tìm kiếm

#### 3.4.2 Xem chi tiết khách hàng
- **Mô tả**: Hiển thị thông tin chi tiết của một khách hàng
- **Thông tin hiển thị**:
  - Thông tin cơ bản (tên, địa chỉ, mã số thuế)
  - Lịch sử thay đổi (SCD2)
  - Danh sách hóa đơn liên quan
  - Thống kê dịch vụ

### 3.5 Báo cáo và Thống kê

#### 3.5.1 Dashboard tổng quan
- **Mô tả**: Hiển thị các thống kê tổng quan trên dashboard
- **Thống kê hiển thị**:
  - Tổng số khách hàng
  - Tổng số tài liệu đã quét
  - Tổng số lượt truy cập

#### 3.5.2 Báo cáo doanh thu
- **Mô tả**: Hiển thị báo cáo doanh thu theo nhiều tiêu chí
- **Báo cáo**:
  - Doanh thu theo khách hàng và theo tháng
  - Doanh thu theo tỉnh/thành phố
  - Biểu đồ cột và biểu đồ tròn

#### 3.5.3 Báo cáo container
- **Mô tả**: Thống kê sử dụng container
- **Thống kê**:
  - Số lượng container theo loại
  - Sử dụng container theo khách hàng
  - Phân bổ container theo tháng

#### 3.5.4 Báo cáo phân bổ địa lý
- **Mô tả**: Thống kê khách hàng và doanh thu theo tỉnh/thành phố
- **Thống kê**:
  - Số lượng khách hàng theo tỉnh
  - Doanh thu theo tỉnh
  - Biểu đồ địa lý

#### 3.5.5 Lọc và làm mới dữ liệu
- **Mô tả**: Người dùng có thể lọc báo cáo và tự động làm mới
- **Tính năng**:
  - Lọc theo khách hàng
  - Lọc theo tháng/năm
  - Tự động làm mới dữ liệu (30s, 1 phút, 5 phút, 15 phút, 30 phút, 1 giờ)
  - Tùy chỉnh khoảng thời gian làm mới

### 3.6 Quản lý Người dùng (Chỉ ADMIN)

#### 3.6.1 Quản lý vai trò
- **Mô tả**: ADMIN có thể quản lý các vai trò trong hệ thống
- **Chức năng**:
  - Xem danh sách vai trò
  - Tạo vai trò mới
  - Chỉnh sửa vai trò
  - Xóa vai trò

#### 3.6.2 Quản lý phòng ban
- **Mô tả**: ADMIN có thể quản lý các phòng ban
- **Chức năng**:
  - Xem danh sách phòng ban
  - Tạo phòng ban mới
  - Chỉnh sửa phòng ban
  - Xóa phòng ban

#### 3.6.3 Quản lý người dùng
- **Mô tả**: ADMIN có thể quản lý tài khoản người dùng
- **Chức năng**:
  - Xem danh sách người dùng
  - Tạo tài khoản mới
  - Chỉnh sửa thông tin người dùng
  - Phân quyền cho người dùng
  - Vô hiệu hóa/kích hoạt tài khoản

### 3.7 API Endpoints

#### 3.7.1 API Xác thực
- `POST /api/login`: Đăng nhập và nhận JWT token
- `POST /api/logout`: Đăng xuất
- `POST /api/register`: Đăng ký tài khoản mới

#### 3.7.2 API OCR
- `POST /ocr/process`: Xử lý OCR cho một file PDF
- `POST /ocr/process-multiple`: Xử lý OCR cho nhiều file PDF
- `POST /ocr/save`: Lưu dữ liệu đã trích xuất vào database

#### 3.7.3 API Thống kê
- `GET /api/customers/count`: Lấy tổng số khách hàng
- `GET /api/documents/count`: Lấy tổng số tài liệu
- `GET /api/visits/count`: Lấy tổng số lượt truy cập

#### 3.7.4 API Tra cứu
- `GET /api/customers/search`: Tìm kiếm khách hàng
- `GET /api/customers/{id}`: Lấy thông tin chi tiết khách hàng

#### 3.7.5 API Báo cáo
- `GET /api/reports/revenue`: Lấy dữ liệu doanh thu
- `GET /api/reports/containers`: Lấy thống kê container
- `GET /api/reports/provinces`: Lấy thống kê theo tỉnh

---

## 4. YÊU CẦU GIAO DIỆN BÊN NGOÀI

### 4.1 Giao diện Người dùng

#### 4.1.1 Yêu cầu chung
- Giao diện web responsive, hỗ trợ nhiều kích thước màn hình
- Thiết kế hiện đại, dễ sử dụng
- Hỗ trợ tiếng Việt
- Tương thích với các trình duyệt: Chrome, Firefox, Edge, Safari

#### 4.1.2 Trang đăng nhập
- Form đăng nhập với username và password
- Hiển thị thông báo lỗi khi đăng nhập sai
- Link đăng ký cho người dùng mới

#### 4.1.3 Trang đăng ký
- Form đăng ký với các trường:
  - Username (bắt buộc)
  - Email (bắt buộc, validate format)
  - Số điện thoại (bắt buộc, 10 số)
  - Họ và tên (bắt buộc)
  - Phòng ban (dropdown, bắt buộc)
  - Password (bắt buộc, tối thiểu 8 ký tự)
  - Confirm Password (bắt buộc)
- Validate real-time
- Hiển thị thông báo lỗi chi tiết

#### 4.1.4 Trang Dashboard
- Hiển thị chào mừng người dùng
- Các card chức năng chính:
  - Quét OCR (chỉ ADMIN và EDITOR)
  - Tra cứu thông tin khách hàng
  - Quản lý vai trò (chỉ ADMIN)
  - Báo cáo Dashboard
- Thống kê nhanh:
  - Tổng số khách hàng
  - Tài liệu đã quét

#### 4.1.5 Trang OCR
- Upload file PDF (drag & drop hoặc chọn file)
- Hỗ trợ upload nhiều file
- Hiển thị tiến trình xử lý
- Hiển thị kết quả trích xuất dưới dạng form có thể chỉnh sửa
- Nút lưu dữ liệu (chỉ ADMIN và EDITOR)

#### 4.1.6 Trang Tra cứu
- Form tìm kiếm với nhiều tiêu chí
- Kết quả tìm kiếm dưới dạng bảng
- Phân trang kết quả
- Xem chi tiết khách hàng

#### 4.1.7 Trang Báo cáo
- Bộ lọc:
  - Lọc theo khách hàng (multi-select)
  - Lọc theo tháng/năm
- Thống kê:
  - Tổng số khách hàng
  - Doanh thu theo khách hàng và tháng (biểu đồ cột)
  - Container theo khách hàng và tháng (biểu đồ cột)
  - Sử dụng container theo khách hàng (biểu đồ tròn)
  - Phân bổ loại container (biểu đồ tròn)
  - Khách hàng theo tỉnh (biểu đồ cột)
  - Doanh thu theo tỉnh (biểu đồ cột)
- Tự động làm mới dữ liệu
- Export dữ liệu (tùy chọn)

### 4.2 Giao diện Phần cứng

Không có yêu cầu giao diện phần cứng đặc biệt.

### 4.3 Giao diện Phần mềm

#### 4.3.1 Database
- **Hệ quản trị**: Microsoft SQL Server
- **Kết nối**: Sử dụng pymssql hoặc pyodbc
- **Cấu trúc**: 
  - Bảng người dùng: users, roles, departments
  - Bảng nghiệp vụ: customers, containers, services, receipts, lines
  - Bảng tham chiếu: provinces, container_types, container_statuses, container_sizes

#### 4.3.2 Web Server
- **Linux/WSL2**: Gunicorn (WSGI server)
- **Windows**: Waitress (HTTP) hoặc Hypercorn (HTTPS)
- **Cấu hình**: 
  - Port: 5000
  - Workers: CPU cores * 2 + 1
  - Timeout: 120 giây

#### 4.3.3 OCR Engine
- **Tesseract OCR**: Engine nhận dạng ký tự
- **Hỗ trợ ngôn ngữ**: Tiếng Việt (vie) và Tiếng Anh (eng)
- **PDF Processing**: pdfplumber, pdf2image

### 4.4 Giao diện Truyền thông

#### 4.4.1 HTTP/HTTPS
- Giao thức: HTTP 1.1, HTTPS (TLS 1.2+)
- Method: GET, POST
- Content-Type: application/json, multipart/form-data, text/html

#### 4.4.2 API Response Format
```json
{
  "success": true/false,
  "data": {...},
  "error": "error message"
}
```

---

## 5. THUỘC TÍNH HỆ THỐNG

### 5.1 Hiệu năng

#### 5.1.1 Thời gian phản hồi
- Trang web: < 2 giây
- API request: < 1 giây
- Xử lý OCR file PDF (10 trang): < 30 giây
- Xử lý OCR nhiều file: < 2 phút cho 10 file

#### 5.1.2 Throughput
- Hỗ trợ tối thiểu 50 request đồng thời
- Xử lý tối đa 10 file PDF đồng thời

#### 5.1.3 Dung lượng
- File PDF tối đa: 50MB
- Tổng dung lượng upload: Không giới hạn (phụ thuộc vào server)

### 5.2 Bảo mật

#### 5.2.1 Xác thực
- Password được mã hóa bằng bcrypt
- Session được quản lý an toàn với HttpOnly và SameSite cookies
- JWT token cho API authentication
- Session timeout: 24 giờ

#### 5.2.2 Phân quyền
- Kiểm tra quyền truy cập ở mọi endpoint
- Role-based access control (RBAC)
- Middleware kiểm tra quyền trước khi xử lý request

#### 5.2.3 Bảo vệ dữ liệu
- SQL injection protection: Sử dụng parameterized queries
- XSS protection: Escape user input
- CSRF protection: SameSite cookies
- HTTPS support: SSL/TLS encryption

#### 5.2.4 Bảo mật file
- Validate file type (chỉ chấp nhận PDF)
- Giới hạn kích thước file
- Lưu trữ file upload trong thư mục riêng biệt

### 5.3 Tính khả dụng

#### 5.3.1 Uptime
- Mục tiêu: 99% uptime
- Thời gian bảo trì: Thông báo trước 24 giờ

#### 5.3.2 Xử lý lỗi
- Hiển thị thông báo lỗi thân thiện với người dùng
- Log lỗi chi tiết cho quản trị viên
- Graceful error handling, không crash hệ thống

### 5.4 Khả năng mở rộng

#### 5.4.1 Mở rộng ngang (Horizontal Scaling)
- Hỗ trợ multiple workers
- Stateless application design
- Database connection pooling

#### 5.4.2 Mở rộng dọc (Vertical Scaling)
- Có thể tăng số workers dựa trên CPU cores
- Database có thể scale độc lập

### 5.5 Khả năng bảo trì

#### 5.5.1 Logging
- Log tất cả lỗi và exception
- Log các thao tác quan trọng (login, OCR processing, data save)
- Log format: Timestamp, Level, Message, Stack trace

#### 5.5.2 Monitoring
- Monitor server health
- Monitor database connections
- Monitor file uploads và OCR processing

### 5.6 Tính di động

- Hệ thống chạy trên web, không cần cài đặt client
- Hỗ trợ nhiều hệ điều hành server: Linux, Windows
- Tương thích với nhiều trình duyệt

---

## 6. CÁC YÊU CẦU KHÁC

### 6.1 Yêu cầu Cơ sở dữ liệu

#### 6.1.1 Cấu trúc Database
- Sử dụng kỹ thuật SCD2 cho bảng customers để lưu lịch sử thay đổi
- Foreign keys để đảm bảo tính toàn vẹn dữ liệu
- Indexes cho các trường thường xuyên tìm kiếm

#### 6.1.2 Backup và Recovery
- Backup database định kỳ (hàng ngày)
- Có thể restore từ backup
- Transaction support cho các thao tác quan trọng

### 6.2 Yêu cầu Cài đặt và Triển khai

#### 6.2.1 Cài đặt
- Hướng dẫn cài đặt chi tiết trong README
- Script tự động cài đặt dependencies
- Cấu hình database và SSL certificates

#### 6.2.2 Triển khai
- Hỗ trợ triển khai trên Linux (WSL2) và Windows
- Script khởi động server tự động
- Cấu hình production-ready

### 6.3 Yêu cầu Tài liệu

#### 6.3.1 Tài liệu Người dùng
- Hướng dẫn sử dụng các chức năng chính
- FAQ (Frequently Asked Questions)
- Video hướng dẫn (tùy chọn)

#### 6.3.2 Tài liệu Kỹ thuật
- API Documentation
- Database Schema
- Architecture Diagram
- Deployment Guide

### 6.4 Yêu cầu Tuân thủ

#### 6.4.1 Tiêu chuẩn
- Tuân thủ chuẩn RESTful API
- Tuân thủ OWASP Top 10 security practices
- Tuân thủ GDPR (nếu áp dụng)

#### 6.4.2 Pháp lý
- Bảo vệ thông tin cá nhân người dùng
- Tuân thủ quy định về bảo mật dữ liệu

### 6.5 Yêu cầu Quốc tế hóa

- Hỗ trợ tiếng Việt (hiện tại)
- Có thể mở rộng hỗ trợ đa ngôn ngữ trong tương lai

---

## PHỤ LỤC

### A. Sơ đồ Use Case

```
┌─────────────┐
│   Người dùng │
└──────┬──────┘
       │
       ├─── Đăng nhập/Đăng ký
       ├─── Xử lý OCR
       ├─── Tra cứu thông tin
       ├─── Xem báo cáo
       └─── Quản lý (ADMIN only)
```

### B. Sơ đồ Luồng Xử lý OCR

```
Upload PDF → Extract Text → Parse Information → 
Save to Database → Display Results
```

### C. Sơ đồ Kiến trúc Hệ thống

```
Client (Browser)
    ↓
Web Server (Gunicorn/Waitress/Hypercorn)
    ↓
Flask Application
    ↓
    ├─── OCR Processor (Tesseract)
    ├─── Database (SQL Server)
    └─── File Storage
```

---

## LỊCH SỬ PHIÊN BẢN

| Phiên bản | Ngày | Mô tả | Tác giả |
|-----------|------|-------|---------|
| 1.0 | 11/12/2025 | Phiên bản đầu tiên | Nhóm phát triển |

---

**Kết thúc tài liệu**

