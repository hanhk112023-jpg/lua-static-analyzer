import unittest
from lua_analyzer.bitvector import BitVector

class TestBitwiseCorpus(unittest.TestCase):
    def test_u8_masking(self):
        self.assertEqual(BitVector.u8(0x1234), 0x34)
        self.assertEqual(BitVector.u8(-1), 0xFF)

    def test_u16_masking(self):
        self.assertEqual(BitVector.u16(0x123456), 0x3456)

    def test_u32_masking(self):
        self.assertEqual(BitVector.u32(0x123456789), 0x23456789)

    def test_bxor_operations(self):
        self.assertEqual(BitVector.bxor(0xAA, 0x55, width=8), 0xFF)
        self.assertEqual(BitVector.bxor(0x1234, 0x1234, width=16), 0x0)

    def test_band_bor_bnot(self):
        self.assertEqual(BitVector.band(0xF0, 0x0F, width=8), 0x0)
        self.assertEqual(BitVector.bor(0xF0, 0x0F, width=8), 0xFF)
        self.assertEqual(BitVector.bnot(0x00, width=8), 0xFF)

    def test_shifts(self):
        self.assertEqual(BitVector.lshift(1, 4, width=8), 16)
        self.assertEqual(BitVector.rshift(16, 2, width=8), 4)

    def test_arithmetic_shift(self):
        # 0x80 is negative in 8-bit
        self.assertEqual(BitVector.arshift(0x80, 1, width=8), 0xC0)
        self.assertEqual(BitVector.arshift(0x40, 1, width=8), 0x20)

    def test_rotations(self):
        self.assertEqual(BitVector.rol(0x80000001, 1, width=32), 0x00000003)
        self.assertEqual(BitVector.ror(0x00000003, 1, width=32), 0x80000001)

    def test_byte_swap32(self):
        self.assertEqual(BitVector.byte_swap32(0x12345678), 0x78563412)

    def test_xor_bytes_repeating_key(self):
        data = b"Hello World"
        key = b"\x42\x13"
        encrypted = BitVector.xor_bytes(data, key)
        decrypted = BitVector.xor_bytes(encrypted, key)
        self.assertEqual(decrypted, data)

    def test_rolling_and_chained_xor(self):
        data = b"Secret Payload"
        rolled = BitVector.rolling_xor(data, initial_key=0x5A, step_add=3, step_mul=5)
        self.assertNotEqual(rolled, data)
        self.assertEqual(len(rolled), len(data))

        chained = BitVector.chained_xor(data, initial_iv=0x11)
        self.assertNotEqual(chained, data)

if __name__ == "__main__":
    unittest.main()
