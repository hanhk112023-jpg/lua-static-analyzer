"""
Audit Reporter Module.
Generates comprehensive security and static deobfuscation Markdown reports.
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
        payload_info = self.results.get("payload_extractor", {})
        opcode_info = self.results.get("opcode_analyzer", {})
        deobf_stats = self.results.get("deobfuscation_stats", {})

        md = f"""# 🛡️ BÁO CÁO PHÂN TÍCH TĨNH & KIỂM ĐỊNH MÃ NGUỒN LUA

* **Tệp phân tích:** `{self.filename}`
* **Thời gian thực hiện:** `{now}`
* **Kích thước tệp:** `{self.filesize:,} bytes`
* **Mã băm SHA-256:** `{self.sha256}`
* **Phân loại chữ ký:** **{vm_info.get('identified_type', 'Unknown')}** (Độ tin cậy: `{vm_info.get('confidence', 0.0) * 100:.1f}%`)

---

## 🌐 1. Điểm Truy Cập Mạng & Trích Xuất URL (Không Thực Thi)
*(Toàn bộ URL được trích xuất bằng phương pháp phân tích tĩnh AST & Regex; hoàn toàn không tải hoặc chạy mã từ Internet)*

"""
        urls = payload_info.get("remote_urls", [])
        if urls:
            for item in urls:
                md += f"- 🔗 **URL:** `{item['url']}` *(Nguồn: {item['source']})*\n"
        else:
            md += "- *(Không phát hiện URL tĩnh trong mã nguồn)*\n"

        md += f"""
---

## ⚡ 2. Cấu Trúc Nạp Động (Loadstring / Evaluator)
"""
        loadstrings = payload_info.get("loadstring_invocations", [])
        if loadstrings:
            for ls in loadstrings[:10]:
                md += f"- ⚠️ `{ls}`\n"
        else:
            md += "- *(Không có cấu trúc nạp động loadstring)*\n"

        md += f"""
---

## 🔬 3. Phân Tích Máy Ảo & Luồng Điều Khiển (VM & Dispatcher Analysis)
* **Phát hiện Dispatcher Loop:** `{'Có' if opcode_info.get('dispatcher_detected') else 'Không'}`
* **Ước tính số lượng Opcodes:** `{opcode_info.get('estimated_opcodes_count', 0)}`
* **Số lượng VM Handlers ghi nhận:** `{len(opcode_info.get('identified_handlers', []))}`
* **Làm phẳng luồng điều khiển (Control Flow Flattening):** `{'Phát hiện cấu trúc máy trạng thái' if vm_info.get('has_dispatcher_loop') else 'Luồng tuần tự chuẩn'}`

---

## 📊 4. Thống Kê Các Phép Biến Đổi Tĩnh
| Phép biến đổi (Transformation) | Số lượng đã xử lý | Ý nghĩa phân tích |
| :--- | :--- | :--- |
| **Ký tự byte thoát thập phân (\\ddd)** | `{deobf_stats.get('escapes_decoded', 0)}` lần | Khôi phục ký tự ASCII an toàn |
| **Ký tự byte thoát Hex (\\x..)** | `{deobf_stats.get('hex_decoded', 0)}` lần | Chuyển đổi mã byte hex thành chuỗi rõ |
| **Gộp nối chuỗi tĩnh (..)** | `{deobf_stats.get('concat_folded', 0)}` lần | Tối giản biểu thức nối hằng chuỗi |
| **Inline Table/Mảng chuỗi hằng** | `{deobf_stats.get('tables_inlined', 0)}` lần | Thay thế tham chiếu bảng chuỗi tĩnh |
| **Tối giản hằng số số học** | `{deobf_stats.get('arithmetic_folded', 0)}` lần | Rút gọn phép tính tĩnh |

---

## ⚠️ 5. Các Giới Hạn Của Phương Pháp Phân Tích Tĩnh
1. **Khóa giải mã động tại runtime:** Với các obfuscator máy ảo phức tạp (như Luraph v15 bytecode VM), bytecode được mã hóa bằng thuật toán dòng bitwise đa tầng tại thời điểm nạp. Phân tích tĩnh có thể bóc tách cấu trúc dispatcher và URL bề mặt nhưng không thể tự động tái tạo 100% tên biến cục bộ gốc đã bị lược bỏ (stripped symbols).
2. **Không thực thi mã (Zero-Execution Policy):** Để đảm bảo an toàn tuyệt đối, hệ thống từ chối nạp hay chạy bất kỳ phần code nào, bảo vệ hoàn toàn môi trường phân tích khỏi mã độc.
"""
        return md
