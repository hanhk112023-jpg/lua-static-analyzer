"""
AST Parser module for Lua.
"""

from typing import List, Optional, Any, Dict
from .lexer import Token, TokenType

class ASTNode:
    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": self.__class__.__name__}

class Program(ASTNode):
    def __init__(self, body: List[ASTNode]):
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "Program", "body": [n.to_dict() for n in self.body]}

class LiteralExpr(ASTNode):
    def __init__(self, value: Any, raw: str):
        self.value = value
        self.raw = raw

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "LiteralExpr", "value": self.value, "raw": self.raw}

class IdentifierExpr(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "IdentifierExpr", "name": self.name}

class BinaryExpr(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "BinaryExpr", "left": self.left.to_dict(), "op": self.op, "right": self.right.to_dict()}

class CallExpr(ASTNode):
    def __init__(self, callee: ASTNode, args: List[ASTNode]):
        self.callee = callee
        self.args = args

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "CallExpr", "callee": self.callee.to_dict(), "args": [a.to_dict() for a in self.args]}

class IndexExpr(ASTNode):
    def __init__(self, obj: ASTNode, index: ASTNode):
        self.obj = obj
        self.index = index

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "IndexExpr", "obj": self.obj.to_dict(), "index": self.index.to_dict()}

class TableExpr(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "TableExpr", "elements": [e.to_dict() for e in self.elements]}

class LocalAssign(ASTNode):
    def __init__(self, names: List[str], values: List[ASTNode]):
        self.names = names
        self.values = values

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "LocalAssign", "names": self.names, "values": [v.to_dict() for v in self.values]}

class Assignment(ASTNode):
    def __init__(self, targets: List[ASTNode], values: List[ASTNode]):
        self.targets = targets
        self.values = values

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "Assignment", "targets": [t.to_dict() for t in self.targets], "values": [v.to_dict() for v in self.values]}

class ReturnStmt(ASTNode):
    def __init__(self, values: List[ASTNode]):
        self.values = values

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": "ReturnStmt", "values": [v.to_dict() for v in self.values]}

class LuaParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in (TokenType.WHITESPACE, TokenType.COMMENT)]
        self.pos = 0

    def peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "", -1, -1)

    def consume(self) -> Token:
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, val: str) -> bool:
        if self.peek().value == val:
            self.consume()
            return True
        return False

    def parse(self) -> Program:
        stmts = []
        while self.peek().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            else:
                self.consume()  # Advance to prevent infinite loop on unhandled syntax
        return Program(stmts)

    def parse_statement(self) -> Optional[ASTNode]:
        tok = self.peek()
        if tok.type == TokenType.KEYWORD:
            if tok.value == "local":
                return self.parse_local()
            elif tok.value == "return":
                self.consume()
                values = []
                while self.peek().type != TokenType.EOF and self.peek().value not in (";", "end", "else", "elseif"):
                    expr = self.parse_expr()
                    if expr:
                        values.append(expr)
                    if not self.match(","):
                        break
                return ReturnStmt(values)
            elif tok.value in ("do", "while", "repeat", "if", "for", "function"):
                # For static analysis, read simple statements
                self.consume()
                return ASTNode()

        # Expression statement or assignment
        expr = self.parse_expr()
        if not expr:
            return None

        if self.peek().value == "=":
            self.consume()
            val = self.parse_expr()
            return Assignment([expr], [val] if val else [])
        return expr

    def parse_local(self) -> Optional[ASTNode]:
        self.consume()  # 'local'
        if self.peek().value == "function":
            self.consume()
            name = self.consume().value
            return LocalAssign([name], [])

        names = []
        while self.peek().type == TokenType.IDENTIFIER:
            names.append(self.consume().value)
            if not self.match(","):
                break

        values = []
        if self.match("="):
            while self.peek().type != TokenType.EOF and self.peek().value not in (";", "end"):
                expr = self.parse_expr()
                if expr:
                    values.append(expr)
                if not self.match(","):
                    break
        self.match(";")
        return LocalAssign(names, values)

    def parse_expr(self) -> Optional[ASTNode]:
        return self.parse_binary(0)

    def parse_binary(self, min_prec: int) -> Optional[ASTNode]:
        left = self.parse_primary()
        if not left:
            return None

        precedences = {
            "or": 1, "and": 2,
            "<": 3, ">": 3, "<=": 3, ">=": 3, "~=": 3, "==": 3,
            "..": 4,
            "+": 5, "-": 5,
            "*": 6, "/": 6, "%": 6,
        }

        while True:
            op = self.peek().value
            if op not in precedences or precedences[op] < min_prec:
                break
            self.consume()
            next_prec = precedences[op] + (0 if op == ".." else 1)  # .. is right-associative
            right = self.parse_binary(next_prec)
            if right:
                left = BinaryExpr(left, op, right)
        return left

    def parse_primary(self) -> Optional[ASTNode]:
        tok = self.peek()
        node = None

        if tok.type == TokenType.NUMBER:
            node = LiteralExpr(float(tok.value) if "." in tok.value else int(tok.value, 0 if "0x" in tok.value.lower() else 10), tok.value)
            self.consume()
        elif tok.type == TokenType.STRING:
            # Strip quotes
            raw = tok.value
            val = raw[1:-1] if raw.startswith(('"', "'")) else raw[2:-2]
            node = LiteralExpr(val, raw)
            self.consume()
        elif tok.type == TokenType.KEYWORD and tok.value in ("true", "false", "nil"):
            val = True if tok.value == "true" else (False if tok.value == "false" else None)
            node = LiteralExpr(val, tok.value)
            self.consume()
        elif tok.type == TokenType.IDENTIFIER:
            node = IdentifierExpr(tok.value)
            self.consume()
        elif tok.value == "(":
            self.consume()
            node = self.parse_expr()
            self.match(")")
        elif tok.value == "{":
            # Table constructor
            self.consume()
            elements = []
            while self.peek().value != "}" and self.peek().type != TokenType.EOF:
                el = self.parse_expr()
                if el:
                    elements.append(el)
                if not (self.match(",") or self.match(";")):
                    break
            self.match("}")
            node = TableExpr(elements)

        if not node:
            return None

        # Postfix: function calls and table indexing
        while True:
            if self.peek().value == "(":
                self.consume()
                args = []
                while self.peek().value != ")" and self.peek().type != TokenType.EOF:
                    arg = self.parse_expr()
                    if arg:
                        args.append(arg)
                    if not self.match(","):
                        break
                self.match(")")
                node = CallExpr(node, args)
            elif self.peek().value == "[":
                self.consume()
                idx = self.parse_expr()
                self.match("]")
                if idx:
                    node = IndexExpr(node, idx)
            elif self.peek().value == ".":
                self.consume()
                id_tok = self.consume()
                node = IndexExpr(node, LiteralExpr(id_tok.value, f'"{id_tok.value}"'))
            elif self.peek().value == ":":
                self.consume()
                method_tok = self.consume()
                node = IndexExpr(node, LiteralExpr(method_tok.value, f'"{method_tok.value}"'))
            else:
                break
        return node
