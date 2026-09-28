import unittest
from lua_analyzer.deobfuscator import LuaDeobfuscator

class TestStringDecoderCorpus(unittest.TestCase):
    def test_single_hex_escape(self):
        deobf = LuaDeobfuscator(r'local s = "\x41"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"A"', cleaned)
        self.assertEqual(stats["hex_decoded"], 1)

    def test_multi_hex_escape(self):
        deobf = LuaDeobfuscator(r'local s = "\x48\x65\x6c\x6c\x6f"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"Hello"', cleaned)
        self.assertEqual(stats["hex_decoded"], 5)

    def test_decimal_escapes(self):
        deobf = LuaDeobfuscator(r'local s = "\087\111\114\108\100"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"World"', cleaned)
        self.assertEqual(stats["escapes_decoded"], 5)

    def test_mixed_escapes(self):
        deobf = LuaDeobfuscator(r'local s = "\x41\066\x43"')
        cleaned, _ = deobf.deobfuscate()
        self.assertIn('"ABC"', cleaned)

    def test_multi_concat(self):
        deobf = LuaDeobfuscator('local s = "a" .. "b" .. "c" .. "d"')
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"abcd"', cleaned)
        self.assertGreaterEqual(stats["concat_folded"], 3)

    def test_table_inlining_sequential(self):
        code = 'local T = {"one", "two", "three"}; print(T[1] .. T[2] .. T[3])'
        deobf = LuaDeobfuscator(code)
        cleaned, _ = deobf.deobfuscate()
        self.assertIn('"onetwothree"', cleaned)

    def test_string_char_folding(self):
        code = 'local s = string.char(70, 79, 79)'
        deobf = LuaDeobfuscator(code)
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"FOO"', cleaned)
        self.assertEqual(stats["string_char_folded"], 1)

    def test_table_concat_folding(self):
        code = 'local s = table.concat({"apple", "banana"})'
        deobf = LuaDeobfuscator(code)
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('"applebanana"', cleaned)
        self.assertEqual(stats["table_concat_folded"], 1)

    def test_constant_arithmetic_within_string_ops(self):
        code = 'local x = 2 * 3; print("val: " .. x)'
        deobf = LuaDeobfuscator(code)
        cleaned, stats = deobf.deobfuscate()
        self.assertIn('6', cleaned)
        self.assertEqual(stats["arithmetic_folded"], 1)

    def test_empty_string_concatenation(self):
        code = 'local s = "" .. "test" .. ""'
        deobf = LuaDeobfuscator(code)
        cleaned, _ = deobf.deobfuscate()
        self.assertIn('"test"', cleaned)

if __name__ == "__main__":
    unittest.main()
