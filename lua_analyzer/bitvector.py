"""
Bitvector Symbolic Engine.
Simulates unsigned 8, 16, and 32-bit bitwise semantics with full precision.
100% Zero-Execution: Operates on numbers, byte sequences, and symbolic expressions.
"""

from typing import Union, List, Optional, Tuple

MASK_8 = 0xFF
MASK_16 = 0xFFFF
MASK_32 = 0xFFFFFFFF

class BitVector:
    """Helper for unsigned bitwise operations with explicit bit widths (8, 16, 32)."""

    @staticmethod
    def u8(val: int) -> int:
        return val & MASK_8

    @staticmethod
    def u16(val: int) -> int:
        return val & MASK_16

    @staticmethod
    def u32(val: int) -> int:
        return val & MASK_32

    @staticmethod
    def bxor(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a ^ b) & mask

    @staticmethod
    def band(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a & b) & mask

    @staticmethod
    def bor(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a | b) & mask

    @staticmethod
    def bnot(a: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (~a) & mask

    @staticmethod
    def lshift(a: int, bits: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a << (bits % width)) & mask

    @staticmethod
    def rshift(a: int, bits: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        val = a & mask
        return (val >> (bits % width)) & mask

    @staticmethod
    def arshift(a: int, bits: int, width: int = 32) -> int:
        """Arithmetic right shift (preserves sign bit)."""
        sign_bit = 1 << (width - 1)
        mask = (1 << width) - 1
        val = a & mask
        shift = bits % width
        if val & sign_bit:
            shifted = (val >> shift) | (mask ^ (mask >> shift))
        else:
            shifted = val >> shift
        return shifted & mask

    @staticmethod
    def rol(a: int, bits: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        val = a & mask
        s = bits % width
        return ((val << s) | (val >> (width - s))) & mask

    @staticmethod
    def ror(a: int, bits: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        val = a & mask
        s = bits % width
        return ((val >> s) | (val << (width - s))) & mask

    @staticmethod
    def add(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a + b) & mask

    @staticmethod
    def sub(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a - b) & mask

    @staticmethod
    def mul(a: int, b: int, width: int = 32) -> int:
        mask = (1 << width) - 1
        return (a * b) & mask

    @staticmethod
    def byte_extract(val: int, byte_idx: int) -> int:
        """Extract nth byte (0-indexed, little endian)."""
        return (val >> (byte_idx * 8)) & MASK_8

    @staticmethod
    def byte_swap32(val: int) -> int:
        v = val & MASK_32
        b0 = (v >> 24) & 0xFF
        b1 = (v >> 8) & 0xFF00
        b2 = (v << 8) & 0xFF0000
        b3 = (v << 24) & 0xFF000000
        return b0 | b1 | b2 | b3

    @staticmethod
    def xor_bytes(data: bytes, key: bytes) -> bytes:
        if not key:
            return data
        res = bytearray(len(data))
        klen = len(key)
        for i, b in enumerate(data):
            res[i] = b ^ key[i % klen]
        return bytes(res)

    @staticmethod
    def rolling_xor(data: bytes, initial_key: int, step_add: int = 0, step_mul: int = 1) -> bytes:
        res = bytearray(len(data))
        k = initial_key & MASK_8
        for i, b in enumerate(data):
            res[i] = b ^ k
            k = (k * step_mul + step_add) & MASK_8
        return bytes(res)

    @staticmethod
    def chained_xor(data: bytes, initial_iv: int = 0) -> bytes:
        res = bytearray(len(data))
        prev = initial_iv & MASK_8
        for i, b in enumerate(data):
            res[i] = b ^ prev
            prev = b
        return bytes(res)
