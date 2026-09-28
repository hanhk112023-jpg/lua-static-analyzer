# 🛡️ Lua Static Analyzer & Audit Tool

Công cụ phân tích tĩnh (Static Analysis) và tái cấu trúc mã nguồn Lua bị làm rối (Obfuscated) chạy trên **CLI** và **GitHub Actions**.

## 🌟 Tính Năng Nổi Bật

- 🔒 **Zero Execution:** Tuyệt đối không thực thi mã nguồn đầu vào và không tải hay chạy bất kỳ script nào từ Internet.
- 🧩 **Giải mã chuỗi tĩnh:** Tự động giải mã byte-escapes (thập phân `\104\116...` và hex `\x68\x74...`).
- 🔗 **Gộp nối chuỗi:** Tối giản các biểu thức hằng chuỗi `..`.
- 🌐 **Trích xuất tĩnh URL & Loader:** Nhận diện và trích xuất URL trong `game:HttpGet(...)`, `loadstring(...)` mà không nạp hay gửi request mạng.
- 📋 **Báo cáo chi tiết:** Tự động xuất file Markdown báo cáo thống kê các phép biến đổi, hash SHA-256 và cảnh báo bảo mật.
- ⚡ **Tự động hóa CI/CD:** Tích hợp sẵn GitHub Actions workflow tự động chạy và xuất artifact + Job Summary.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Chạy thủ công trên CLI
```bash
python3 lua_analyzer.py <đường_dẫn_file.lua> -o output/
```

### 2. Chạy tự động qua GitHub Actions
1. Vào tab **Actions** trên GitHub.
2. Chọn workflow **Lua Static Analyzer & Audit**.
3. Nhấn **Run workflow**, nhập đường dẫn file Lua cần kiểm tra.
4. Xem kết quả trực tiếp tại **Job Summary** hoặc tải kết quả trong mục **Artifacts**.
