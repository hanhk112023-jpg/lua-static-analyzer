import unittest
from lua_analyzer.deobfuscator import LuaDeobfuscator

class TestDeobfuscator(unittest.TestCase):
    def test_decode_decimal_escapes(self):
        deobf = LuaDeobfuscator(r'local s = "\104\101\108\108\111"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"hello"', cleaned)
        self.assertEqual(stats["escapes_decoded"], 5)

    def test_decode_hex_escapes(self):
        deobf = LuaDeobfuscator(r'local s = "\x61\x70\x69"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"api"', cleaned)
        self.assertEqual(stats["hex_decoded"], 3)

    def test_fold_concatenations(self):
        deobf = LuaDeobfuscator('local s = "hello " .. "world" .. "!"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"hello world!"', cleaned)
        self.assertGreaterEqual(stats["concat_folded"], 2)

    def test_inline_string_tables(self):
        code = 'local T = {"cat", "dog"}; print(T[1], T[2])'
        deobf = LuaDeobfuscator(code)
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"cat"', cleaned)
        self.assertIn('"dog"', cleaned)
        self.assertEqual(stats["tables_inlined"], 2)

    def test_fold_simple_arithmetic(self):
        code = 'local x = 15 + 25'
        deobf = LuaDeobfuscator(code)
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('40', cleaned)
        self.assertEqual(stats["arithmetic_folded"], 1)

if __name__ == "__main__":
    unittest.main()
