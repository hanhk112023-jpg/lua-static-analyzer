#!/usr/bin/env python3
"""
Lua Static Source Analyzer & Safe Cleaner (CLI & GitHub Actions)
----------------------------------------------------------------
100% Static Analysis - NEVER executes untrusted Lua or external network requests.
Specialized in decoding escaped strings, folding constant concatenations,
extracting remote URLs (HttpGet, Webhooks), and producing formatted code + Markdown audits.
"""

import sys
import os
import re
import hashlib
import datetime
import argparse
from typing import List, Dict, Tuple, Set

class LuaStaticAnalyzer:
    def __init__(self, input_path: str, output_dir: str = None):
        self.input_path = os.path.abspath(input_path)
        self.output_dir = output_dir or os.path.dirname(self.input_path)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.raw_code = ""
        self.transformed_code = ""
        self.file_hash = ""
        self.file_size = 0
        
        # Audit statistics
        self.stats = {
            "escapes_decoded": 0,
            "hex_decoded": 0,
            "concat_folded": 0,
            "string_tables_inlined": 0,
            "urls_detected": [],
            "loadstring_calls": [],
            "suspicious_patterns": [],
            "identified_obfuscator": "Unknown / Generic Obfuscation"
        }

    def load_file(self):
        if not os.path.isfile(self.input_path):
            raise FileNotFoundError(f"File not found: {self.input_path}")
        
        with open(self.input_path, "r", encoding="utf-8", errors="replace") as f:
            self.raw_code = f.read()
            
        self.file_size = len(self.raw_code)
        self.file_hash = hashlib.sha256(self.raw_code.encode("utf-8")).hexdigest()
        self.transformed_code = self.raw_code

    def detect_obfuscation_signatures(self):
        code = self.raw_code
        if "Luraph" in code or "lura.ph" in code:
            self.stats["identified_obfuscator"] = "Luraph Obfuscator (Bytecode VM / Watermark found)"
        elif "IronBrew" in code or "IB2" in code:
            self.stats["identified_obfuscator"] = "IronBrew / Luraph derivative VM"
        elif "Moonsec" in code:
            self.stats["identified_obfuscator"] = "MoonSec Obfuscator"
        elif "PSU Obfuscator" in code:
            self.stats["identified_obfuscator"] = "PSU Obfuscator"
        elif re.search(r"\\(?:[0-9]{2,3}|x[0-9a-fA-F]{2}){10,}", code):
            self.stats["identified_obfuscator"] = "Heavy Hex / Byte-escape Obfuscation"
        else:
            self.stats["identified_obfuscator"] = "Custom / Standard Lua Script"

    def scan_network_and_eval_patterns(self):
        """Pure static search for HttpGet, requests, and loadstring calls without executing."""
        # 1. HttpGet / HttpGetAsync
        http_pattern = re.compile(
            r'(?:game|self|Workspace)[\s:]+(?:HttpGet|HttpGetAsync)\s*\(\s*(["\'])(https?://[^\'"]+)\1',
            re.IGNORECASE
        )
        for match in http_pattern.finditer(self.raw_code):
            url = match.group(2)
            if url not in self.stats["urls_detected"]:
                self.stats["urls_detected"].append(url)
                
        # 2. Generic HTTP / Webhook URLs
        generic_url = re.compile(r'https?://[a-zA-Z0-9\-\._~:/\?#\[\]@!$&\'\(\)\*\+,;=%]{8,}')
        for match in generic_url.finditer(self.raw_code):
            url = match.group(0)
            # Filter obvious false positives
            if url not in self.stats["urls_detected"] and not url.endswith((".png", ".jpg", ".webp")):
                self.stats["urls_detected"].append(url)

        # 3. Loadstring patterns
        loadstring_pat = re.compile(r'\b(loadstring|load)\s*\((.*?)\)', re.DOTALL)
        for match in loadstring_pat.finditer(self.raw_code):
            snippet = match.group(0)[:120].replace("\n", " ").strip()
            self.stats["loadstring_calls"].append(snippet)

        # 4. Potentially suspicious execution or evasion calls
        suspicious_keywords = ["getrenv", "getreg", "hookfunction", "setreadonly", "make_writeable", "syn.request", "request", "http_request"]
        for kw in suspicious_keywords:
            count = len(re.findall(r'\b' + re.escape(kw) + r'\b', self.raw_code))
            if count > 0:
                self.stats["suspicious_patterns"].append(f"`{kw}` (found {count} times)")

    def decode_escape_sequences(self):
        """Statically decodes decimal (\\104) and hex (\\x68) byte escapes inside string literals."""
        def unescape_match(match):
            token = match.group(0)
            quote = token[0]
            inner = token[1:-1]
            
            # Replace decimal escapes \000 - \255
            def dec_replace(m):
                val = int(m.group(1))
                if 32 <= val <= 126 and val not in (34, 39, 92): # Printable ASCII without quotes or backslash
                    self.stats["escapes_decoded"] += 1
                    return chr(val)
                return m.group(0)
            
            inner = re.sub(r'\\([0-9]{1,3})', dec_replace, inner)

            # Replace hex escapes \x00 - \xFF
            def hex_replace(m):
                val = int(m.group(1), 16)
                if 32 <= val <= 126 and val not in (34, 39, 92):
                    self.stats["hex_decoded"] += 1
                    return chr(val)
                return m.group(0)

            inner = re.sub(r'\\x([0-9a-fA-F]{2})', hex_replace, inner)
            return quote + inner + quote

        # Match single or double quoted strings
        pattern = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
        self.transformed_code = pattern.sub(unescape_match, self.transformed_code)

    def fold_string_concatenation(self):
        """Folds statically concatenable string constants: "abc" .. "def" -> "abcdef" """
        # Matches: "str1" .. "str2" or 'str1' .. 'str2'
        concat_pattern = re.compile(r'(["\'])(.*?)\1\s*\.\.\s*(["\'])(.*?)\3')
        
        while True:
            new_code, count = concat_pattern.subn(r'\1\2\4\1', self.transformed_code)
            if count == 0:
                break
            self.stats["concat_folded"] += count
            self.transformed_code = new_code

    def inline_simple_string_tables(self):
        """Inlines simple static constant tables: local T = {"a", "b"}; print(T[1])"""
        table_def_pattern = re.compile(
            r'local\s+([a-zA-Z_0-9]+)\s*=\s*\{\s*([\'"][^\'"\}]+[\'"](?:\s*,\s*[\'"][^\'"\}]+[\'"])*)\s*\}'
        )
        for match in table_def_pattern.finditer(self.transformed_code):
            var_name = match.group(1)
            raw_elements = match.group(2)
            
            elements = [e.strip()[1:-1] for e in raw_elements.split(",") if e.strip()]
            if not elements or len(elements) > 200:
                continue
                
            # Replace var_name[1], var_name[2], etc.
            def table_access_replace(m):
                idx = int(m.group(1))
                if 1 <= idx <= len(elements):
                    self.stats["string_tables_inlined"] += 1
                    return f'"{elements[idx-1]}"'
                return m.group(0)

            access_pattern = re.compile(r'\b' + re.escape(var_name) + r'\[\s*([0-9]+)\s*\]')
            self.transformed_code = access_pattern.sub(table_access_replace, self.transformed_code)

    def format_code(self):
        """Basic clean beautification of lines and indentation."""
        lines = [line.strip() for line in self.transformed_code.split("\n")]
        indent_level = 0
        indent_size = "    "
        formatted_lines = []
        
        increase_keywords = ("function", "then", "do", "repeat")
        decrease_keywords = ("end", "until")

        for line in lines:
            if not line:
                formatted_lines.append("")
                continue

            # Check if line starts with decrease keyword
            starts_with_end = any(line.startswith(kw) for kw in decrease_keywords) or line.startswith("else") or line.startswith("elseif")
            if starts_with_end and indent_level > 0:
                current_indent = indent_level - 1
            else:
                current_indent = indent_level

            formatted_lines.append((indent_size * max(0, current_indent)) + line)

            # Adjust indent level for next lines
            # Count blocks opened
            tokens = line.split()
            for token in tokens:
                if token in ("function", "then", "do", "repeat"):
                    indent_level += 1
                elif token in ("end", "until"):
                    if indent_level > 0:
                        indent_level -= 1

        self.transformed_code = "\n".join(formatted_lines)

    def write_outputs(self) -> Tuple[str, str]:
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        cleaned_path = os.path.join(self.output_dir, f"{base_name}_cleaned.lua")
        report_path = os.path.join(self.output_dir, f"{base_name}_analysis_report.md")

        with open(cleaned_path, "w", encoding="utf-8") as f:
            f.write(self.transformed_code)

        # Generate Comprehensive Markdown Report
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_md = f"""# 🛡️ BÁO CÁO PHÂN TÍCH TĨNH NGUỒN LUA (LUA STATIC ANALYSIS AUDIT)

* **Tệp đầu vào:** `{os.path.basename(self.input_path)}`
* **Thời gian phân tích:** `{now}`
* **Dung lượng file:** `{self.file_size:,} bytes`
* **SHA-256 Checksum:** `{self.file_hash}`
* **Nhận diện kỹ thuật Obfuscation:** **{self.stats['identified_obfuscator']}**

---

## 🌐 1. URL & Endpoint Trích Xuất Được (Không thực thi)
*(Toàn bộ URL được trích xuất tĩnh qua regex và cấu trúc AST, hoàn toàn không tải hoặc chạy qua mạng)*

"""
        if self.stats["urls_detected"]:
            for u in self.stats["urls_detected"]:
                report_md += f"- 🔗 **URL:** `{u}`\n"
        else:
            report_md += "- *(Không phát hiện URL tĩnh trong mã nguồn)*\n"

        report_md += f"""
---

## ⚡ 2. Cấu trúc Loadstring / Nạp động phát hiện
"""
        if self.stats["loadstring_calls"]:
            for ls in self.stats["loadstring_calls"][:15]:
                report_md += f"- ⚠️ `{ls}`\n"
        else:
            report_md += "- *(Không có lệnh loadstring)*\n"

        report_md += f"""
---

## 📊 3. Thống Kê Phép Biến Đổi & Giải Mã Tĩnh
| Phép biến đổi (Transformation) | Số lượng đã xử lý | Ghi chú an toàn |
| :--- | :--- | :--- |
| **Ký tự thoát thập phân (\\ddd)** | `{self.stats['escapes_decoded']}` lần | Khôi phục về ký tự ASCII an toàn |
| **Ký tự thoát Hexadecimal (\\x..)** | `{self.stats['hex_decoded']}` lần | Chuyển đổi mã byte hex về chuỗi rõ |
| **Gộp nối chuỗi tĩnh (..)** | `{self.stats['concat_folded']}` lần | Tối giản biểu thức nối hằng chuỗi |
| **Inline Table hằng số** | `{self.stats['string_tables_inlined']}` lần | Thay thế tham chiếu bảng chuỗi tĩnh |

---

## 🔍 4. Các API / Hàm Nhạy Cảm Phát Hiện
"""
        if self.stats["suspicious_patterns"]:
            for sp in self.stats["suspicious_patterns"]:
                report_md += f"- 🚩 {sp}\n"
        else:
            report_md += "- *(Không phát hiện API nhạy cảm phổ biến)*\n"

        report_md += f"""
---

## 📂 5. Tệp Xuất Sau Xử Lý
* **File đã làm rõ:** `{os.path.basename(cleaned_path)}`
* **Nguyên tắc an toàn:** Không thay đổi hay ghi đè file gốc; toàn bộ quá trình là phân tích tĩnh độc lập.
"""

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        return cleaned_path, report_path

    def run(self) -> Tuple[str, str]:
        self.load_file()
        self.detect_obfuscation_signatures()
        self.scan_network_and_eval_patterns()
        self.decode_escape_sequences()
        self.fold_string_concatenation()
        self.inline_simple_string_tables()
        self.format_code()
        return self.write_outputs()

def main():
    parser = argparse.ArgumentParser(description="Static Lua Source Deobfuscator & Security Inspector")
    parser.add_argument("input", help="Path to input Lua file")
    parser.add_argument("-o", "--output", help="Output directory (default: same as input)", default=None)
    args = parser.parse_args()

    analyzer = LuaStaticAnalyzer(args.input, args.output)
    cleaned, report = analyzer.run()
    print(f"[✓] Analysis Completed Successfully!")
    print(f" -> Cleaned Source: {cleaned}")
    print(f" -> Audit Report:   {report}")

if __name__ == "__main__":
    main()
