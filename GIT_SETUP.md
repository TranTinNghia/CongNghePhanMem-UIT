# Hướng dẫn đưa code lên Git lần đầu

## Bước 1: Cài đặt Git (nếu chưa có)

### Windows:
1. Tải Git từ: https://git-scm.com/download/win
2. Cài đặt với các tùy chọn mặc định

### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt install git

# Mac
brew install git
```

## Bước 2: Cấu hình Git lần đầu

Mở Terminal/Command Prompt và chạy:

```bash
# Cấu hình tên
git config --global user.name "Tên của bạn"

# Cấu hình email
git config --global user.email "email@example.com"

# Kiểm tra cấu hình
git config --list
```

## Bước 3: Khởi tạo Git repository trong project

Mở Terminal/Command Prompt trong thư mục project (`BaiTapNhom`):

```bash
# Di chuyển vào thư mục project
cd /mnt/d/UIT/Software/BaiTapNhom

# Khởi tạo Git repository
git init

# Kiểm tra trạng thái
git status
```

## Bước 4: Tạo file .gitignore (đã có sẵn)

File `.gitignore` đã được tạo để bỏ qua các file không cần thiết:
- `config/config.yaml` (chứa password)
- `__pycache__/`
- `venv/`
- `uploads/`
- v.v.

## Bước 5: Tạo file config.yaml từ template

**QUAN TRỌNG**: Trước khi commit, cần tạo file `config.yaml` từ template:

```bash
# Copy file mẫu
cp config/config.yaml.example config/config.yaml

# Chỉnh sửa file config.yaml với thông tin database thực tế của bạn
# (File này sẽ KHÔNG được commit lên Git vì đã có trong .gitignore)
```

## Bước 6: Thêm các file vào Git

```bash
# Xem các file sẽ được thêm
git status

# Thêm tất cả các file (trừ những file trong .gitignore)
git add .

# Hoặc thêm từng file cụ thể:
# git add app.py
# git add requirements.txt
# git add templates/
# git add static/
# v.v.
```

## Bước 7: Commit lần đầu

```bash
# Commit với message
git commit -m "Initial commit: Flask application with OCR, dashboard, and user management"

# Xem lịch sử commit
git log
```

## Bước 8: Tạo repository trên GitHub

1. Đăng nhập vào [GitHub.com](https://github.com)
2. Click nút **"+"** ở góc trên bên phải → **"New repository"**
3. Điền thông tin:
   - **Repository name**: `BaiTapNhom` (hoặc tên khác)
   - **Description**: "Flask application for OCR processing and dashboard reporting"
   - **Visibility**: 
     - **Public**: Ai cũng xem được (miễn phí)
     - **Private**: Chỉ bạn và người được mời xem được (có thể cần trả phí)
   - **KHÔNG** tích vào "Initialize this repository with a README" (vì đã có code)
4. Click **"Create repository"**

## Bước 9: Kết nối local repository với GitHub

Sau khi tạo repository trên GitHub, bạn sẽ thấy hướng dẫn. Chạy các lệnh sau:

```bash
# Thêm remote repository (thay YOUR_USERNAME và REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Hoặc nếu dùng SSH:
# git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# Kiểm tra remote đã thêm chưa
git remote -v
```

## Bước 10: Push code lên GitHub

```bash
# Đổi tên branch chính thành main (nếu cần)
git branch -M main

# Push code lên GitHub
git push -u origin main
```

Nếu lần đầu, GitHub sẽ yêu cầu đăng nhập:
- **Username**: Tên GitHub của bạn
- **Password**: Sử dụng Personal Access Token (không phải password GitHub)
  - Tạo token tại: https://github.com/settings/tokens
  - Chọn "Generate new token (classic)"
  - Chọn quyền: `repo` (full control)
  - Copy token và dùng làm password

## Bước 11: Kiểm tra trên GitHub

1. Vào repository trên GitHub
2. Kiểm tra các file đã được upload
3. Đảm bảo **KHÔNG** có file `config/config.yaml` (vì đã được ignore)

## Các lệnh Git thường dùng sau này

```bash
# Xem trạng thái
git status

# Xem các thay đổi
git diff

# Thêm file đã sửa
git add .

# Commit với message
git commit -m "Mô tả thay đổi"

# Push lên GitHub
git push

# Pull code mới nhất từ GitHub
git pull

# Xem lịch sử commit
git log --oneline

# Tạo branch mới
git checkout -b feature/new-feature

# Chuyển về branch main
git checkout main

# Merge branch
git merge feature/new-feature
```

## Lưu ý quan trọng

### ✅ Nên commit:
- Code Python (.py)
- Templates HTML
- Static files (CSS, JS, images)
- Requirements.txt
- README.md
- Các file cấu hình không chứa thông tin nhạy cảm

### ❌ KHÔNG commit:
- `config/config.yaml` (chứa password database)
- `__pycache__/` (Python cache)
- `venv/` hoặc `env/` (Virtual environment)
- `uploads/` (Files người dùng upload)
- `.env` (Environment variables)
- File log

### 🔒 Bảo mật:
- **KHÔNG BAO GIỜ** commit password, API keys, hoặc thông tin nhạy cảm
- Sử dụng `.gitignore` để tự động bỏ qua các file nhạy cảm
- Nếu vô tình commit password, cần:
  1. Đổi password ngay lập tức
  2. Xóa file khỏi Git history (dùng `git filter-branch` hoặc `git-filter-repo`)

## Troubleshooting

### Lỗi: "fatal: remote origin already exists"
```bash
# Xóa remote cũ
git remote remove origin

# Thêm lại
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Lỗi: "failed to push some refs"
```bash
# Pull code mới nhất trước
git pull origin main --allow-unrelated-histories

# Sau đó push lại
git push -u origin main
```

### Quên commit file
```bash
# Thêm file vào commit trước
git add forgotten-file.py

# Sửa commit cuối cùng (chưa push)
git commit --amend --no-edit

# Hoặc tạo commit mới
git commit -m "Add forgotten file"
```

### Muốn xóa file đã commit nhầm
```bash
# Xóa file khỏi Git (nhưng giữ file trên máy)
git rm --cached config/config.yaml

# Commit thay đổi
git commit -m "Remove config.yaml from Git"

# Push lên
git push
```

## Tóm tắt các lệnh cần thiết

```bash
# 1. Khởi tạo
git init

# 2. Cấu hình (chỉ cần làm 1 lần)
git config --global user.name "Tên của bạn"
git config --global user.email "email@example.com"

# 3. Thêm file
git add .

# 4. Commit
git commit -m "Initial commit"

# 5. Thêm remote
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 6. Push
git push -u origin main
```

## Tiếp theo

Sau khi code đã lên GitHub, bạn có thể:
1. Deploy lên Render/Railway (xem file `DEPLOY.md`)
2. Mời các thành viên khác vào repository
3. Tạo các branch để phát triển tính năng mới
4. Sử dụng Issues và Pull Requests để quản lý dự án

