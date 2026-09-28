import unittest
from lua_analyzer.constants import ConstExpr, ConstantPool, SymbolicConstantEvaluator

class TestConstantDecoderCorpus(unittest.TestCase):
    def test_eval_concat(self):
        expr = ConstExpr("CONCAT", [ConstExpr("STRING", ["foo"]), ConstExpr("STRING", ["bar"])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, "foobar")

    def test_eval_add(self):
        expr = ConstExpr("ADD", [ConstExpr("NUMBER", [10]), ConstExpr("NUMBER", [25])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 35)

    def test_eval_sub(self):
        expr = ConstExpr("SUB", [ConstExpr("NUMBER", [100]), ConstExpr("NUMBER", [45])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 55)

    def test_eval_mul(self):
        expr = ConstExpr("MUL", [ConstExpr("NUMBER", [6]), ConstExpr("NUMBER", [7])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 42)

    def test_eval_xor_bytes(self):
        expr = ConstExpr("XOR", [ConstExpr("LITERAL", [b"\x00\xFF"]), ConstExpr("LITERAL", [b"\xAA\xAA"])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, b"\xAA\x55")

    def test_eval_rol(self):
        expr = ConstExpr("ROL", [ConstExpr("NUMBER", [1]), ConstExpr("NUMBER", [4])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 16)

    def test_eval_ror(self):
        expr = ConstExpr("ROR", [ConstExpr("NUMBER", [16]), ConstExpr("NUMBER", [2])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 4)

    def test_eval_index_table(self):
        tbl = ["alpha", "beta", "gamma"]
        expr = ConstExpr("INDEX", [ConstExpr("LITERAL", [tbl]), ConstExpr("NUMBER", [2])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, "beta")

    def test_eval_string_char(self):
        expr = ConstExpr("STRING_CHAR", [ConstExpr("LITERAL", [[72, 101, 108, 108, 111]])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, "Hello")

    def test_eval_byte_extract(self):
        expr = ConstExpr("BYTE_EXTRACT", [ConstExpr("NUMBER", [0x12345678]), ConstExpr("NUMBER", [1])])
        res, ok, _ = SymbolicConstantEvaluator.evaluate(expr)
        self.assertTrue(ok)
        self.assertEqual(res, 0x56)

    def test_non_constant_dependency(self):
        # A non-constant leaf node
        unknown_node = ConstExpr("DYNAMIC_VAR", ["runtime_var"])
        expr = ConstExpr("ADD", [ConstExpr("NUMBER", [10]), unknown_node])
        res, ok, reason = SymbolicConstantEvaluator.evaluate(expr)
        self.assertFalse(ok)
        self.assertIn("non_constant_dependency", res)

if __name__ == "__main__":
    unittest.main()
