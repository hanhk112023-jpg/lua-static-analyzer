"""
Audit Reporter Module.
Generates comprehensive security, provenance, and static devirtualization Markdown reports.
"""

import datetime
from typing import Dict, Any

class AuditReporter:
    def __init__(self, filename: str, filesize: int, sha256: str, analysis_results: Dict[str, Any]):
        self.filename = filename
        self.filesize = filesize
        self.sha256 = sha256
        self.results = analysis_results

    def generate_markdown(self) -> str:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        vm_info = self.results.get("vm_detector", {})
        vm_boundary = self.results.get("vm_boundary", {})
        soa_info = self.results.get("soa", {})
        payload_info = self.results.get("payload_extractor", {})
        opcode_info = self.results.get("opcode_analyzer", {})
        deobf_stats = self.results.get("deobfuscation_stats", {})
        cfg_info = self.results.get("cfg", {})
        coverage = self.results.get("deobfuscation_coverage", {})

        md = f"""# 🛡️ BÁO CÁO PHÂN TÍCH TĨNH & DEVIRTUALIZATION NGUỒN LUA

* **Tệp phân tích:** `{self.filename}`
* **Thời gian kiểm định:** `{now}`
* **Kích thước tệp:** `{self.filesize:,} bytes`
* **Mã băm SHA-256:** `{self.sha256}`
* **Phân loại kiến trúc:** **{vm_info.get('identified_type', 'Unknown')}** (Độ tin cậy: `{vm_info.get('confidence', 0.0) * 100:.1f}%`)

---

## 🌐 1. Điểm Truy Cập Mạng & Payload Extracted (Không Thực Thi)
*(Mọi URL được trích xuất bằng phương pháp phân tích tĩnh ngữ nghĩa AST/Regex; tuyệt đối không gửi request mạng)*

"""
        urls = payload_info.get("remote_urls", [])
        if urls:
            for item in urls:
                md += (
                    f"- 🔗 **URL:** `{item['resolved_value']}`\n"
                    f"  - *Phương pháp:* `{item['resolution_method']}` | *Độ tin cậy:* `{item['confidence'] * 100:.1f}%`\n"
                    f"  - *Biểu thức gốc:* `{item['original_expression']}`\n"
                )
        else:
            md += "- *(Không phát hiện URL tĩnh trong mã nguồn)*\n"

        md += f"""
---

## ⚡ 2. Cấu Trúc Nạp Động & Thực Thi Mã (Loadstring)
"""
        loadstrings = payload_info.get("loadstring_invocations", [])
        if loadstrings:
            for ls in loadstrings[:10]:
                md += f"- ⚠️ `{ls}`\n"
        else:
            md += "- *(Không có lệnh nạp động loadstring)*\n"

        md += f"""
---

## 🔬 3. Kiến Trúc Máy Ảo & VM Boundary Recovery
* **Bộ điều phối (Dispatcher):** `{vm_boundary.get('dispatcher_type', 'None')}`
* **Vị trí Program Counter (PC):** `{vm_boundary.get('pc_location', 'None')}`
* **Mảng thanh ghi ảo (Virtual Registers):** `{vm_boundary.get('register_location', 'None')}`
* **Cấu trúc Structure-of-Arrays (SoA):** `{'Phát hiện SoA layout' if soa_info.get('arrays') else 'None'}`
* **Biến chỉ mục dùng chung:** `{', '.join(soa_info.get('shared_index_vars', [])) or 'None'}`

---

## 📊 4. Thống Kê Phép Biến Đổi & Khôi Phục Hằng Số
| Phép biến đổi (Transformation) | Số lượng đã xử lý | Ghi chú kỹ thuật |
| :--- | :--- | :--- |
| **Ký tự thoát thập phân (\\ddd)** | `{deobf_stats.get('escapes_decoded', 0)}` lần | Khôi phục ký tự ASCII an toàn |
| **Ký tự thoát Hex (\\x..)** | `{deobf_stats.get('hex_decoded', 0)}` lần | Chuyển đổi mã byte hex thành chuỗi rõ |
| **Gộp nối chuỗi tĩnh (..)** | `{deobf_stats.get('concat_folded', 0)}` lần | Tối giản biểu thức nối hằng chuỗi |
| **Gộp hàm string.char(...)** | `{deobf_stats.get('string_char_folded', 0)}` lần | Rút gọn mảng số thành chuỗi ký tự |
| **Gộp hàm table.concat(...)** | `{deobf_stats.get('table_concat_folded', 0)}` lần | Nối mảng hằng chuỗi tĩnh |
| **Inline Table/Mảng chuỗi hằng** | `{deobf_stats.get('tables_inlined', 0)}` lần | Thay thế truy cập mảng tĩnh |
| **Tối giản phép tính số học** | `{deobf_stats.get('arithmetic_folded', 0)}` lần | Rút gọn hằng số số học |

---

## 📈 5. Độ Bao Phủ Phân Tích (Deobfuscation Coverage)
| Chỉ tiêu phân tích | Tỷ lệ bao phủ ước tính |
| :--- | :--- |
| **Prototype Recovery** | `{coverage.get('prototype_recovery', 'N/A')}` |
| **Constant Recovery** | `{coverage.get('constant_recovery', 'N/A')}` |
| **Opcode Recovery** | `{coverage.get('opcode_recovery', 'N/A')}` |
| **CFG Normalization** | `{coverage.get('cfg_recovery', 'N/A')}` |
| **String Recovery** | `{coverage.get('string_recovery', 'N/A')}` |

---

## ⚠️ 6. Các Giới Hạn Của Phương Pháp Phân Tích Tĩnh
1. **Zero-Execution Guarantee:** Hệ thống đảm bảo 100% không thực thi mã nguồn đầu vào. Các giá trị phụ thuộc hoàn toàn vào trạng thái ngẫu nhiên tại runtime (như timestamp, tick count, server challenge) được gắn nhãn `Dynamic value unresolved`.
2. **VM Bytecode Stripped:** Các tên định danh biến cục bộ ban đầu bị xóa trong quá trình biên dịch bytecode được thay thế bằng tên định danh ngữ nghĩa chuẩn (`var_1`, `decoded_url`, v.v.).
"""
        return md
