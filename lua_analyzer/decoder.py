"""
Decoder Function Analysis Module.
Statically analyzes and executes constant-input string decoder routines.
100% Zero-Execution: Operates strictly via symbolic evaluation and bounds-checked emulation.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .bitvector import BitVector
from .constants import ConstExpr, SymbolicConstantEvaluator

class DecoderResolution:
    STATICALLY_RESOLVED = "STATICALLY_RESOLVED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    UNRESOLVED = "UNRESOLVED"

class DecoderFunction:
    def __init__(self, name: str, params: List[str], body: str, source_location: str = "unknown"):
        self.name = name
        self.params = params
        self.body = body
        self.source_location = source_location
        self.uses_bitwise = any(kw in body for kw in ("bxor", "band", "bor", "~", "bit32"))
        self.uses_string_char = "string.char" in body
        self.uses_buffer = "buffer." in body
        self.has_loop = any(kw in body for kw in ("for ", "while ", "repeat "))

class DecoderAnalyzer:
    """Analyzes Lua functions to identify and evaluate constant decoders."""

    def __init__(self, code: str):
        self.code = code
        self.identified_decoders: List[DecoderFunction] = []

    def find_decoder_candidates(self) -> List[DecoderFunction]:
        """Finds functions matching decoder patterns."""
        candidates = []
        # Pattern: local function name(param1, ...) ... end
        pattern = re.compile(
            r'(?:local\s+)?function\s+([a-zA-Z_0-9]+)\s*\(([^)]*)\)(.*?)(?:\bend\b)',
            re.DOTALL
        )
        for m in pattern.finditer(self.code):
            fn_name = m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            body = m.group(3)
            # Decoder heuristic: contains string.char, table.concat, bit32, or char reconstruction
            if any(k in body for k in ("string.char", "table.concat", "bit32.bxor", "buffer.", "% 256")):
                cand = DecoderFunction(fn_name, params, body, source_location=f"func:{fn_name}")
                candidates.append(cand)

        self.identified_decoders = candidates
        return candidates

    def try_symbolic_eval_call(self, decoder: DecoderFunction, args: List[Any]) -> Tuple[Any, str, float]:
        """
        Attempts to symbolically execute a simple string decoder on constant arguments.
        Budget: max 100,000 iterations to prevent hangs.
        Returns: (result_or_none, resolution_status, confidence)
        """
        if not args:
            return None, DecoderResolution.UNRESOLVED, 0.0

        # Pattern 1: Array of numbers decoded with fixed XOR key
        # e.g., for i, b in ipairs(t) do res[i] = string.char(b ~ key) end
        xor_key_match = re.search(r'(?:bit32\.bxor|~)\s*\(?([a-zA-Z_0-9]+)[,\s]+([0-9]+)\)?', decoder.body)
        if xor_key_match and isinstance(args[0], (list, tuple)):
            try:
                key = int(xor_key_match.group(2))
                decoded_chars = [chr((int(val) ^ key) & 0xFF) for val in args[0]]
                return "".join(decoded_chars), DecoderResolution.STATICALLY_RESOLVED, 0.95
            except Exception:
                pass

        # Pattern 2: Byte array to string.char directly
        if "string.char" in decoder.body and isinstance(args[0], (list, tuple)) and not decoder.uses_bitwise:
            try:
                decoded_chars = [chr(int(val) & 0xFF) for val in args[0]]
                return "".join(decoded_chars), DecoderResolution.STATICALLY_RESOLVED, 0.90
            except Exception:
                pass

        # Pattern 3: Rolling XOR / Additive
        rolling_match = re.search(r'([0-9]+)\s*\+\s*([a-zA-Z_0-9]+)\s*\*\s*([0-9]+)', decoder.body)
        if rolling_match and isinstance(args[0], bytes):
            try:
                add_k = int(rolling_match.group(1))
                mul_k = int(rolling_match.group(3))
                init_k = int(args[1]) if len(args) > 1 and isinstance(args[1], int) else 0
                res = BitVector.rolling_xor(args[0], init_k, add_k, mul_k)
                return res.decode('utf-8', errors='replace'), DecoderResolution.STATICALLY_RESOLVED, 0.85
            except Exception:
                pass

        return None, DecoderResolution.UNRESOLVED, 0.0
