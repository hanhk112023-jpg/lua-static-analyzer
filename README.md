# 🛡️ Lua Static Analyzer & Deobfuscation Toolkit

Công cụ phân tích tĩnh (Static Analysis) và tái cấu trúc mã nguồn Lua bị làm rối (Obfuscated) chạy trên **CLI** và **GitHub Actions**.

## 🌟 Kiến Trúc Pipeline Kỹ Thuật

```
Lua input
  ↓
Lexer / Parser (Tokenization & AST Generation)
  ↓
Static Analyzer (Scope & Symbol Tracking)
  ↓
VM Detector (Luraph, IronBrew, MoonSec, PSU, Flattened Dispatcher Detection)
  ↓
Payload Extractor (HttpGet, Remote URLs, Webhooks, Loadstring, Base64 Blobs - Zero Execution)
  ↓
Opcode Analyzer (Dispatcher Trees, Handler Mappings, State Transitions)
  ↓
IR Generator (Intermediate Representation: LOADK, CALL, GETTABLE, JMP...)
  ↓
Control Flow Analysis (CFG Basic Blocks & Dispatcher Flattening Detection)
  ↓
Deobfuscator (Hex/Decimal Byte Unescaping, String Concat Folding, Table Inlining)
  ↓
Pseudo-Lua Reconstruction (Clean Code Formatting & Proper Indentation)
  ↓
Markdown Audit Report (SHA-256, Extracted URLs, Security Flags, Statistics)
```

---

## 🔒 Nguyên Tắc An Toàn (Zero-Execution)
- Tuyệt đối **không gọi `loadstring`** hoặc chạy Lua bytecode.
- Toàn bộ URL và payload từ bên ngoài được xử lý hoàn toàn dưới dạng dữ liệu tĩnh, **không gửi request mạng**.
- File đầu vào luôn được bảo vệ nguyên trạng, không ghi đè file gốc.

---

## 🚀 Hướng Dẫn Sử Dụng

### 1. Cài đặt & Chạy thủ công trên CLI
```bash
# Cài đặt
pip install -e .

# Chạy phân tích
python cli.py samples/sample_loader.lua -o output/
```

### 2. Chạy tự động qua GitHub Actions
Quy trình CI (`.github/workflows/ci.yml`) tự động:
1. Cài đặt dependencies và package.
2. Chạy toàn bộ Unit Tests & Integration Tests (`python -m unittest discover`).
3. Chạy pipeline phân tích trên toàn bộ file mẫu trong `samples/`.
4. Xác minh sự tồn tại và tính hợp lệ của tất cả file output (`_cleaned.lua`, `_analysis_report.md`, `_ir.txt`).
5. Xuất báo cáo Markdown trực tiếp lên **GitHub Job Summary**.
6. Lưu trữ toàn bộ kết quả phân tích trong mục **Artifacts** (lưu 7 ngày).
