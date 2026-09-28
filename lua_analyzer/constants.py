"""
Constant Recovery & Symbolic Evaluation Module.
Implements ConstExpr, Symbolic Evaluator with strict provenance and confidence tracking.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from .bitvector import BitVector

class ConstExpr:
    """Represents a symbolic or concrete constant expression."""

    def __init__(self, op: str, operands: List[Any], provenance: Optional[Dict[str, Any]] = None):
        self.op = op
        self.operands = operands
        self.provenance = provenance or {"method": "literal", "confidence": 1.0, "source": "static"}

    def is_concrete(self) -> bool:
        if self.op in ("LITERAL", "STRING", "NUMBER", "BOOLEAN", "NIL"):
            return True
        return False

    def get_value(self) -> Any:
        if self.op in ("LITERAL", "STRING", "NUMBER", "BOOLEAN", "NIL"):
            return self.operands[0]
        return None

    def __repr__(self) -> str:
        if self.is_concrete():
            return f"Const({repr(self.operands[0])})"
        return f"{self.op}({', '.join(repr(o) for o in self.operands)})"

class ConstantPool:
    """Stores recovered constant pool values and expressions for a prototype or module."""

    def __init__(self, pool_id: str = "main"):
        self.pool_id = pool_id
        self.constants: List[ConstExpr] = []
        self.named_constants: Dict[str, ConstExpr] = {}

    def add(self, expr: ConstExpr) -> int:
        idx = len(self.constants)
        self.constants.append(expr)
        return idx

    def set_named(self, name: str, expr: ConstExpr):
        self.named_constants[name] = expr

    def get(self, idx: int) -> Optional[ConstExpr]:
        if 0 <= idx < len(self.constants):
            return self.constants[idx]
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pool_id": self.pool_id,
            "count": len(self.constants),
            "constants": [
                {
                    "index": i,
                    "op": c.op,
                    "value": c.get_value() if c.is_concrete() else repr(c),
                    "provenance": c.provenance
                }
                for i, c in enumerate(self.constants)
            ]
        }

class SymbolicConstantEvaluator:
    """Zero-Execution symbolic evaluation of ConstExpr trees."""

    @staticmethod
    def evaluate(expr: Any) -> Tuple[Any, bool, Optional[str]]:
        """
        Evaluates expr statically.
        Returns: (result_value_or_expr, is_fully_resolved, unknown_reason)
        """
        if not isinstance(expr, ConstExpr):
            # Already raw python literal (int, str, bool, etc.)
            return expr, True, None

        if expr.is_concrete():
            return expr.operands[0], True, None

        op = expr.op
        eval_operands = []
        for o in expr.operands:
            val, resolved, reason = SymbolicConstantEvaluator.evaluate(o)
            if not resolved:
                return f"unknown(reason=\"non_constant_dependency: {reason}\")", False, reason
            eval_operands.append(val)

        try:
            if op == "CONCAT":
                return str(eval_operands[0]) + str(eval_operands[1]), True, None

            elif op == "XOR":
                a, b = eval_operands[0], eval_operands[1]
                if isinstance(a, bytes) and isinstance(b, bytes):
                    return BitVector.xor_bytes(a, b), True, None
                elif isinstance(a, int) and isinstance(b, int):
                    return BitVector.bxor(a, b), True, None
                elif isinstance(a, list) and isinstance(b, int):
                    return [b_val ^ b for b_val in a], True, None
                return f"unknown(reason=\"unsupported_types_for_xor\")", False, "unsupported_types"

            elif op == "ADD":
                return BitVector.add(int(eval_operands[0]), int(eval_operands[1])), True, None

            elif op == "SUB":
                return BitVector.sub(int(eval_operands[0]), int(eval_operands[1])), True, None

            elif op == "MUL":
                return BitVector.mul(int(eval_operands[0]), int(eval_operands[1])), True, None

            elif op == "ROL":
                return BitVector.rol(int(eval_operands[0]), int(eval_operands[1])), True, None

            elif op == "ROR":
                return BitVector.ror(int(eval_operands[0]), int(eval_operands[1])), True, None

            elif op == "INDEX":
                tbl, idx = eval_operands[0], eval_operands[1]
                if isinstance(tbl, (list, tuple)):
                    # 1-indexed (Lua convention) or 0-indexed fallback
                    i = int(idx)
                    if 1 <= i <= len(tbl):
                        return tbl[i - 1], True, None
                    elif 0 <= i < len(tbl):
                        return tbl[i], True, None
                elif isinstance(tbl, dict):
                    if idx in tbl:
                        return tbl[idx], True, None
                return f"unknown(reason=\"index_out_of_bounds\")", False, "index_out_of_bounds"

            elif op == "STRING_CHAR":
                # converts integers into ASCII string
                chars = []
                for num in eval_operands:
                    if isinstance(num, list):
                        for sub_n in num:
                            chars.append(chr(int(sub_n) & 0xFF))
                    else:
                        chars.append(chr(int(num) & 0xFF))
                return "".join(chars), True, None

            elif op == "BYTE_EXTRACT":
                val, b_idx = int(eval_operands[0]), int(eval_operands[1])
                return BitVector.byte_extract(val, b_idx), True, None

        except Exception as e:
            return f"unknown(reason=\"evaluation_error: {str(e)}\")", False, str(e)

        return f"unknown(reason=\"unhandled_operator: {op}\")", False, f"unhandled_operator_{op}"
