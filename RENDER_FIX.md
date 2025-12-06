# Hướng dẫn sửa lỗi Python version trên Render

## Vấn đề
Render đang cài Python 3.13.4 thay vì 3.10.12 như đã chỉ định trong `runtime.txt`

## Giải pháp

### Cách 1: Chỉ định Python version trong Render Dashboard (Khuyến nghị)

1. Vào [Render Dashboard](https://dashboard.render.com)
2. Chọn Web Service của bạn
3. Vào tab **"Settings"**
4. Scroll xuống phần **"Environment"**
5. Tìm **"Python Version"** hoặc **"Build Command"**
6. Thêm vào Build Command:
   ```bash
   python3.10 -m pip install -r requirements.txt
   ```
   Hoặc chỉ định Python version trong Environment Variables:
   - Key: `PYTHON_VERSION`
   - Value: `3.10.12`

7. Click **"Save Changes"**
8. Vào tab **"Manual Deploy"** → Click **"Deploy latest commit"**

### Cách 2: Sử dụng Python 3.13 (Đã cập nhật Pillow)

Đã cập nhật `requirements.txt` để Pillow tương thích với Python 3.13:
- Pillow từ `==10.1.0` → `>=10.2.0`

Bạn có thể:
1. Xóa hoặc comment dòng Python version trong Settings
2. Để Render dùng Python 3.13 mặc định
3. Rebuild lại

### Cách 3: Tạo Build Script

Tạo file `build.sh`:

```bash
#!/bin/bash
# Install Python 3.10
pyenv install 3.10.12
pyenv local 3.10.12

# Install dependencies
pip install -r requirements.txt
```

Sau đó trong Render Dashboard:
- **Build Command**: `chmod +x build.sh && ./build.sh`

## Kiểm tra

Sau khi rebuild, kiểm tra logs:
- Python version phải là 3.10.12
- Không còn lỗi build Pillow

## Lưu ý

- Render có thể không đọc `runtime.txt` như Heroku
- Cần chỉ định Python version trong Dashboard hoặc dùng build script
- File `render.yaml` chỉ hoạt động khi deploy qua Blueprint (tự động)

