"""
Lexer module for Lua source code tokenization.
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    EOF = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

LUA_KEYWORDS = {
    "and", "break", "do", "else", "elseif", "end", "false", "for",
    "function", "if", "in", "local", "nil", "not", "or", "repeat",
    "return", "then", "true", "until", "while"
}

class LuaLexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(code)

    def tokenize(self, keep_comments: bool = False, keep_whitespace: bool = False) -> List[Token]:
        tokens = []
        while self.pos < self.length:
            # Check comment
            if self.code.startswith("--", self.pos):
                token = self._read_comment()
                if keep_comments:
                    tokens.append(token)
                continue

            # Check whitespace
            if self.code[self.pos].isspace():
                token = self._read_whitespace()
                if keep_whitespace:
                    tokens.append(token)
                continue

            # Multi-line string [[ ... ]]
            if self.code.startswith("[[", self.pos):
                tokens.append(self._read_long_string())
                continue

            # Normal string "..." or '...'
            if self.code[self.pos] in ('"', "'"):
                tokens.append(self._read_string())
                continue

            # Number (hex, float, int)
            if self.code[self.pos].isdigit() or (self.code[self.pos] == '.' and self.pos + 1 < self.length and self.code[self.pos + 1].isdigit()):
                tokens.append(self._read_number())
                continue

            # Identifier or Keyword
            if self.code[self.pos].isalpha() or self.code[self.pos] == '_':
                tokens.append(self._read_identifier())
                continue

            # Two or three char operators
            for op in ("...", "..", "==", "~=", "<=", ">=", "+=", "-=", "*=", "/="):
                if self.code.startswith(op, self.pos):
                    start_col = self.col
                    self.pos += len(op)
                    self.col += len(op)
                    tokens.append(Token(TokenType.OPERATOR if op != "..." else TokenType.PUNCTUATION, op, self.line, start_col))
                    break
            else:
                # Single char operator or punctuation
                ch = self.code[self.pos]
                start_col = self.col
                self.pos += 1
                self.col += 1
                if ch in "+-*/%^#=<>()[]{},;:.":
                    t_type = TokenType.OPERATOR if ch in "+-*/%^#=<>~" else TokenType.PUNCTUATION
                    tokens.append(Token(t_type, ch, self.line, start_col))
                else:
                    # Unknown / symbol
                    tokens.append(Token(TokenType.PUNCTUATION, ch, self.line, start_col))

        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens

    def _read_comment(self) -> Token:
        start_line, start_col = self.line, self.col
        self.pos += 2
        self.col += 2
        if self.code.startswith("[[", self.pos):
            # Long comment
            self.pos += 2
            self.col += 2
            end_idx = self.code.find("]]", self.pos)
            if end_idx == -1:
                content = self.code[self.pos:]
                self.pos = self.length
            else:
                content = self.code[self.pos:end_idx]
                self.pos = end_idx + 2
            # update lines
            self.line += content.count("\n")
            return Token(TokenType.COMMENT, f"--[[{content}]]", start_line, start_col)
        else:
            # Single line comment
            end_idx = self.code.find("\n", self.pos)
            if end_idx == -1:
                content = self.code[self.pos:]
                self.pos = self.length
            else:
                content = self.code[self.pos:end_idx]
                self.pos = end_idx
            return Token(TokenType.COMMENT, f"--{content}", start_line, start_col)

    def _read_whitespace(self) -> Token:
        start_line, start_col = self.line, self.col
        start_pos = self.pos
        while self.pos < self.length and self.code[self.pos].isspace():
            if self.code[self.pos] == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1
        return Token(TokenType.WHITESPACE, self.code[start_pos:self.pos], start_line, start_col)

    def _read_string(self) -> Token:
        start_line, start_col = self.line, self.col
        quote = self.code[self.pos]
        self.pos += 1
        self.col += 1
        chars = [quote]
        escaped = False
        while self.pos < self.length:
            ch = self.code[self.pos]
            chars.append(ch)
            self.pos += 1
            self.col += 1
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                break
        return Token(TokenType.STRING, "".join(chars), start_line, start_col)

    def _read_long_string(self) -> Token:
        start_line, start_col = self.line, self.col
        self.pos += 2
        self.col += 2
        end_idx = self.code.find("]]", self.pos)
        if end_idx == -1:
            content = self.code[self.pos:]
            self.pos = self.length
        else:
            content = self.code[self.pos:end_idx]
            self.pos = end_idx + 2
        self.line += content.count("\n")
        return Token(TokenType.STRING, f"[[{content}]]", start_line, start_col)

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        start_pos = self.pos
        # Hex
        if self.code.startswith(("0x", "0X"), self.pos):
            self.pos += 2
            self.col += 2
            while self.pos < self.length and (self.code[self.pos].isdigit() or self.code[self.pos].lower() in "abcdef"):
                self.pos += 1
                self.col += 1
        else:
            # Decimal or float
            has_dot = False
            while self.pos < self.length:
                ch = self.code[self.pos]
                if ch.isdigit():
                    self.pos += 1
                    self.col += 1
                elif ch == '.' and not has_dot:
                    has_dot = True
                    self.pos += 1
                    self.col += 1
                else:
                    break
        return Token(TokenType.NUMBER, self.code[start_pos:self.pos], start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line, start_col = self.line, self.col
        start_pos = self.pos
        while self.pos < self.length and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
            self.pos += 1
            self.col += 1
        val = self.code[start_pos:self.pos]
        token_type = TokenType.KEYWORD if val in LUA_KEYWORDS else TokenType.IDENTIFIER
        return Token(token_type, val, start_line, start_col)
