import unittest
from lua_analyzer.lexer import LuaLexer, TokenType
from lua_analyzer.parser import LuaParser, LiteralExpr, BinaryExpr, CallExpr

class TestLexerParser(unittest.TestCase):
    def test_lexer_tokens(self):
        code = 'local a = 123 + "hello"'
        lexer = LuaLexer(code)
        tokens = [t for t in lexer.tokenize() if t.type != TokenType.EOF]
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].value, "local")
        self.assertEqual(tokens[1].value, "a")
        self.assertEqual(tokens[2].value, "=")
        self.assertEqual(tokens[3].value, "123")
        self.assertEqual(tokens[4].value, "+")
        self.assertEqual(tokens[5].value, '"hello"')

    def test_parser_binary(self):
        code = 'local x = 10 + 20 * 2'
        lexer = LuaLexer(code)
        parser = LuaParser(lexer.tokenize())
        prog = parser.parse()
        self.assertEqual(len(prog.body), 1)

    def test_parser_call(self):
        code = 'print("hello", 42)'
        lexer = LuaLexer(code)
        parser = LuaParser(lexer.tokenize())
        prog = parser.parse()
        self.assertEqual(len(prog.body), 1)
        self.assertIsInstance(prog.body[0], CallExpr)

if __name__ == "__main__":
    unittest.main()
