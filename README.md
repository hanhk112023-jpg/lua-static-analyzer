# 🛡️ Lua Static Analyzer & Devirtualization Toolkit

Công cụ phân tích tĩnh (Static Analysis) và devirtualization mã nguồn Lua/Luau bị làm rối (Obfuscated) chạy trên **CLI** và **GitHub Actions**.
Tuân thủ nguyên tắc **100% Zero-Execution**: Tuyệt đối không nạp, không chạy untrusted code hoặc payload từ Internet.

---

## 🌟 Kiến Trúc Pipeline Toàn Diện

```
Input Lua/Luau
  ↓
Lexer & Parser (AST Construction)
  ↓
Protection & VM Signature Detection (Luraph, IronBrew, MoonSec, PSU, Dispatcher)
  ↓
VM Boundary Detection (VMLayout: pc, registers, stack, state variables)
  ↓
Structure-of-Arrays (SoA) Recovery (Opcode[], OperandA[], OperandB[], OperandC[], Constants[])
  ↓
Prototype Extraction & Graph (Bootstrap, Anti-Tamper, Decoder, VM Runtime, Payload)
  ↓
Constant Recovery & Symbolic Evaluation (ConstExpr: ADD, SUB, MUL, XOR, ROL, ROR, INDEX, STRING_CHAR)
  ↓
Bitvector Symbolic Engine (8/16/32-bit unsigned bitwise emulation)
  ↓
Decoder Function Analysis (Loop/Table/Bitwise static decoding)
  ↓
Opcode Recovery & Semantic Inference (LOADK, MOVE, CALL, RETURN, GETTABLE, SETTABLE, JMP, ADD)
  ↓
Virtual Register Dataflow & Reaching Definitions
  ↓
SSA & Sparse Conditional Constant Propagation (SCCP Branch Pruning)
  ↓
Control Flow Graph (CFG) Analysis & Normalization (Irreducible Graph Splitting, Natural Loops)
  ↓
Dispatcher Devirtualization (Unrolling State Machines & Binary Decision Trees)
  ↓
Semantic Payload Extractor (URLs, Loadstrings, Base64 with Provenance)
  ↓
Deobfuscator (Byte Escapes \ddd, \x.., Concat Folding, string.char, table.concat, Table Inlining)
  ↓
Pseudo-Lua Reconstruction (Clean Formatting, 4-space Indentation, Idiomatic Syntax)
  ↓
Markdown Security Report & Multi-Artifact Export
```

---

## 🚀 Hướng Dẫn Sử Dụng CLI

```bash
# Cài đặt
pip install -e .

# Phân tích tĩnh cơ bản
python cli.py samples/sample_loader.lua -o output/

# Chạy phân tích sâu & devirtualization với đầy đủ tùy chọn
python cli.py samples/sample_loader.lua -o output/ \
    --deep \
    --vm-analysis \
    --dump-prototypes \
    --dump-constants \
    --dump-opcodes \
    --dump-cfg \
    --dump-ir \
    --strict-static
```

---

## 📦 Danh Mục Artifact Xuất Ra Mỗi Lần Phân Tích
Với mỗi file `.lua` đầu vào, công cụ tự động sinh ra 8 file độc lập:
1. `<name>_cleaned.lua`: Mã nguồn Pseudo-Lua đã khử rối và định dạng sạch.
2. `<name>_analysis_report.md`: Báo cáo kiểm định Markdown chi tiết (SHA-256, độ bao phủ, URL trích xuất, chữ ký VM).
3. `<name>_ir.txt`: Mã trung gian độc lập kiến trúc (Intermediate Representation).
4. `<name>_cfg.json`: Cấu trúc đồ thị luồng điều khiển (CFG Basic Blocks, Edges, Loops, Flattening).
5. `<name>_prototypes.json`: Cây phân cấp và vai trò Prototype.
6. `<name>_constants.json`: Thống kê các phép biến đổi hằng số.
7. `<name>_opcodes.json`: Bảng ánh xạ Opcode và ngữ nghĩa suy diễn.
8. `<name>_symbolic.json`: Trạng thái lan truyền hằng số biểu tượng (SCCP).

---

## 🧪 Bộ Kiểm Thử (Regression Test Suite)
Hệ thống tích hợp **100 bài kiểm thử** tự động bao gồm:
* 11 bài kiểm thử Bitvector (XOR, Rolling XOR, Rotations, Shifts, Byte Swap)
* 11 bài kiểm thử Constant Decoder & ConstExpr
* 10 bài kiểm thử String Decoder & Escapes
* 10 bài kiểm thử Dispatcher Devirtualization
* 10 bài kiểm thử CFG & Loop Detection
* 10 bài kiểm thử Opcode Semantic Inference
* 10 bài kiểm thử Prototype Graph & Classification
* 10 bài kiểm thử Phủ định (False Positives Prevention)
* Kiểm thử Sandbox (Monkeypatch chặn socket, urllib, subprocess, os.system)
* Kiểm thử tính tất định (Determinism Check: cùng input sinh ra bit-exact output)
