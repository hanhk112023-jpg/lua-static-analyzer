"""
Deobfuscator Module.
Performs safe static transformations:
- Unescaping decimal and hexadecimal bytes
- Folding constant string concatenations
- Folding string.char(...) calls with constant numbers
- Folding table.concat(...) calls with constant string arrays
- Inlining static string array/lookup tables
- Constant folding for arithmetic expressions
"""

import re
from typing import Dict, Any, Tuple

class LuaDeobfuscator:
    def __init__(self, code: str):
        self.code = code
        self.stats = {
            "escapes_decoded": 0,
            "hex_decoded": 0,
            "concat_folded": 0,
            "tables_inlined": 0,
            "arithmetic_folded": 0,
            "string_char_folded": 0,
            "table_concat_folded": 0
        }

    def deobfuscate(self) -> Tuple[str, Dict[str, int]]:
        code = self.code
        code = self.decode_escapes(code)
        code = self.fold_string_char(code)
        code = self.fold_table_concat(code)
        code = self.fold_concatenations(code)
        code = self.inline_string_tables(code)
        code = self.fold_simple_arithmetic(code)
        code = self.fold_string_char(code)
        # Run second pass for concatenated strings from inlined tables
        code = self.fold_concatenations(code)
        return code, self.stats

    def decode_escapes(self, code: str) -> str:
        """Decodes decimal (\\104) and hex (\\x68) byte escapes inside string literals."""
        def unescape_match(match):
            token = match.group(0)
            quote = token[0]
            inner = token[1:-1]

            # 1. Decimal escapes \000 - \255
            def dec_replace(m):
                val = int(m.group(1))
                if 32 <= val <= 126 and val not in (34, 39, 92):
                    self.stats["escapes_decoded"] += 1
                    return chr(val)
                return m.group(0)

            inner = re.sub(r'\\([0-9]{1,3})', dec_replace, inner)

            # 2. Hex escapes \x00 - \xFF
            def hex_replace(m):
                val = int(m.group(1), 16)
                if 32 <= val <= 126 and val not in (34, 39, 92):
                    self.stats["hex_decoded"] += 1
                    return chr(val)
                return m.group(0)

            inner = re.sub(r'\\x([0-9a-fA-F]{2})', hex_replace, inner)
            return quote + inner + quote

        pattern = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
        return pattern.sub(unescape_match, code)

    def fold_string_char(self, code: str) -> str:
        """Folds string.char(c1, c2, ...) when all arguments are static numbers."""
        char_pattern = re.compile(r'string\.char\s*\(\s*([0-9\s,]+)\s*\)')
        def char_replace(m):
            raw_nums = m.group(1)
            nums = [n.strip() for n in raw_nums.split(",") if n.strip()]
            chars = []
            for n in nums:
                try:
                    val = int(n)
                    if 0 <= val <= 255:
                        chars.append(chr(val))
                    else:
                        return m.group(0)
                except ValueError:
                    return m.group(0)
            self.stats["string_char_folded"] += 1
            # Escape internal double quotes if needed
            escaped_str = "".join(chars).replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped_str}"'

        return char_pattern.sub(char_replace, code)

    def fold_table_concat(self, code: str) -> str:
        """Folds table.concat({"a", "b", "c"}) -> "abc" """
        concat_pattern = re.compile(
            r'table\.concat\s*\(\s*\{\s*([\'"][^\'"\}]+[\'"](?:\s*,\s*[\'"][^\'"\}]+[\'"])*)\s*\}\s*\)'
        )
        def concat_replace(m):
            raw_elements = m.group(1)
            elements = [e.strip()[1:-1] for e in raw_elements.split(",") if e.strip()]
            self.stats["table_concat_folded"] += 1
            folded = "".join(elements).replace('\\', '\\\\').replace('"', '\\"')
            return f'"{folded}"'

        return concat_pattern.sub(concat_replace, code)

    def fold_concatenations(self, code: str) -> str:
        """Folds statically concatenable strings: "foo" .. "bar" -> "foobar" """
        concat_pattern = re.compile(r'(["\'])(.*?)\1\s*\.\.\s*(["\'])(.*?)\3')
        while True:
            new_code, count = concat_pattern.subn(r'\1\2\4\1', code)
            if count == 0:
                break
            self.stats["concat_folded"] += count
            code = new_code
        return code

    def inline_string_tables(self, code: str) -> str:
        """Inlines simple static lookup tables: local T = {"a", "b"}; use T[1]"""
        table_def_pattern = re.compile(
            r'local\s+([a-zA-Z_0-9]+)\s*=\s*\{\s*([\'"][^\'"\}]+[\'"](?:\s*,\s*[\'"][^\'"\}]+[\'"])*)\s*\}'
        )
        for match in table_def_pattern.finditer(code):
            var_name = match.group(1)
            raw_elements = match.group(2)
            elements = [e.strip()[1:-1] for e in raw_elements.split(",") if e.strip()]
            if not elements or len(elements) > 300:
                continue

            def table_access_replace(m):
                idx = int(m.group(1))
                if 1 <= idx <= len(elements):
                    self.stats["tables_inlined"] += 1
                    return f'"{elements[idx-1]}"'
                return m.group(0)

            access_pattern = re.compile(r'\b' + re.escape(var_name) + r'\[\s*([0-9]+)\s*\]')
            code = access_pattern.sub(table_access_replace, code)
        return code

    def fold_simple_arithmetic(self, code: str) -> str:
        """Folds constant arithmetic: e.g. (10 + 20) -> 30"""
        def arith_replace(m):
            num1 = int(m.group(1))
            op = m.group(2)
            num2 = int(m.group(3))
            res = None
            if op == "+":
                res = num1 + num2
            elif op == "-":
                res = num1 - num2
            elif op == "*":
                res = num1 * num2
            if res is not None:
                self.stats["arithmetic_folded"] += 1
                return str(res)
            return m.group(0)

        pattern = re.compile(r'\b([0-9]{1,6})\s*([\+\-\*])\s*([0-9]{1,6})\b')
        code = pattern.sub(arith_replace, code)
        return code
