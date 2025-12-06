# Hướng dẫn cấu hình Python 3.10.12 trên Render

## Vấn đề
Render mặc định dùng Python 3.13, nhưng bạn muốn dùng Python 3.10.12.

## Giải pháp: Chỉ định trong Render Dashboard

### Bước 1: Vào Settings
1. Đăng nhập [Render Dashboard](https://dashboard.render.com)
2. Chọn Web Service của bạn
3. Click tab **"Settings"**

### Bước 2: Thêm Environment Variable
1. Scroll xuống phần **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Thêm:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.10.12`
4. Click **"Save Changes"**

### Bước 3: Cập nhật Build Command
1. Trong phần **"Build Command"**, thay đổi từ:
   ```
   pip install -r requirements.txt
   ```
   
   Thành:
   ```
   python3.10 -m pip install --upgrade pip && python3.10 -m pip install -r requirements.txt
   ```
   
   Hoặc nếu không có python3.10, dùng:
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

2. Click **"Save Changes"**

### Bước 4: Rebuild
1. Vào tab **"Manual Deploy"**
2. Click **"Deploy latest commit"**
3. Xem logs để đảm bảo Python version là 3.10.12

## Kiểm tra

Sau khi rebuild, kiểm tra logs:
- Tìm dòng: `Using Python version 3.10.12`
- Hoặc: `Python 3.10.12`

## Lưu ý

- Render có thể không tự động detect Python version từ `runtime.txt`
- Cần chỉ định rõ ràng trong Environment Variables hoặc Build Command
- Nếu vẫn không được, thử dùng build script (`build.sh`)

## Alternative: Sử dụng Build Script

Nếu cách trên không hoạt động, có thể dùng build script:

1. Trong **Build Command**, thay bằng:
   ```
   chmod +x build.sh && ./build.sh
   ```

2. File `build.sh` đã được tạo sẵn trong repository

