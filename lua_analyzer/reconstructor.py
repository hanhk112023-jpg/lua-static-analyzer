"""
Pseudo-Lua Reconstructor Module.
Beautifies and formats AST or deobfuscated tokens into clean, idiomatic Lua code.
"""

from typing import List

class PseudoLuaReconstructor:
    def __init__(self, code: str, indent_size: str = "    "):
        self.code = code
        self.indent_size = indent_size

    def reconstruct(self) -> str:
        lines = [l.strip() for l in self.code.split("\n")]
        indent_level = 0
        formatted_lines = []

        increase_keywords = ("function", "then", "do", "repeat")
        decrease_keywords = ("end", "until")

        for line in lines:
            if not line:
                formatted_lines.append("")
                continue

            # Check if line begins with a dedent keyword
            starts_with_dedent = (
                any(line.startswith(kw) for kw in decrease_keywords) or
                line.startswith("else") or
                line.startswith("elseif")
            )
            current_indent = max(0, indent_level - 1 if starts_with_dedent else indent_level)
            formatted_lines.append((self.indent_size * current_indent) + line)

            # Calculate indentation changes
            tokens = line.split()
            for token in tokens:
                if token in increase_keywords:
                    indent_level += 1
                elif token in decrease_keywords:
                    if indent_level > 0:
                        indent_level -= 1

        return "\n".join(formatted_lines)
