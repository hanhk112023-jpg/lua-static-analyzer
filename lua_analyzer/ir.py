"""
Intermediate Representation (IR) Module.
Lifts AST nodes and VM instructions into architecture-independent IR.
"""

from typing import List, Dict, Any, Optional

class Opcode:
    LOADK = "LOADK"
    MOVE = "MOVE"
    GETGLOBAL = "GETGLOBAL"
    SETGLOBAL = "SETGLOBAL"
    GETTABLE = "GETTABLE"
    SETTABLE = "SETTABLE"
    BINARY_OP = "BINARY_OP"
    CALL = "CALL"
    RETURN = "RETURN"
    JMP = "JMP"
    JMP_IF_FALSE = "JMP_IF_FALSE"

class IRInstruction:
    def __init__(self, op: str, dest: Optional[str] = None, arg1: Any = None, arg2: Any = None, comment: str = ""):
        self.op = op
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.comment = comment

    def __str__(self) -> str:
        parts = [f"{self.op:<12}"]
        if self.dest:
            parts.append(f"{self.dest} =")
        if self.arg1 is not None:
            parts.append(str(self.arg1))
        if self.arg2 is not None:
            parts.append(str(self.arg2))
        if self.comment:
            parts.append(f"; {self.comment}")
        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "dest": self.dest,
            "arg1": str(self.arg1) if self.arg1 is not None else None,
            "arg2": str(self.arg2) if self.arg2 is not None else None,
            "comment": self.comment
        }

class IRGenerator:
    def __init__(self):
        self.instructions: List[IRInstruction] = []
        self._reg_counter = 0

    def new_reg(self) -> str:
        self._reg_counter += 1
        return f"R{self._reg_counter}"

    def emit(self, op: str, dest: Optional[str] = None, arg1: Any = None, arg2: Any = None, comment: str = "") -> IRInstruction:
        instr = IRInstruction(op, dest, arg1, arg2, comment)
        self.instructions.append(instr)
        return instr

    def lift_ast(self, node: Any) -> Optional[str]:
        """Lifts basic AST expressions into linear IR instructions."""
        from .parser import LiteralExpr, IdentifierExpr, BinaryExpr, CallExpr, IndexExpr, LocalAssign, Assignment

        if isinstance(node, LiteralExpr):
            reg = self.new_reg()
            self.emit(Opcode.LOADK, dest=reg, arg1=node.raw, comment=f"literal {type(node.value).__name__}")
            return reg

        elif isinstance(node, IdentifierExpr):
            reg = self.new_reg()
            self.emit(Opcode.GETGLOBAL, dest=reg, arg1=node.name)
            return reg

        elif isinstance(node, BinaryExpr):
            left_reg = self.lift_ast(node.left)
            right_reg = self.lift_ast(node.right)
            reg = self.new_reg()
            self.emit(Opcode.BINARY_OP, dest=reg, arg1=f"{left_reg} {node.op}", arg2=right_reg)
            return reg

        elif isinstance(node, CallExpr):
            callee_reg = self.lift_ast(node.callee)
            arg_regs = [self.lift_ast(arg) for arg in node.args]
            reg = self.new_reg()
            self.emit(Opcode.CALL, dest=reg, arg1=callee_reg, arg2=f"({', '.join(str(r) for r in arg_regs)})")
            return reg

        elif isinstance(node, IndexExpr):
            obj_reg = self.lift_ast(node.obj)
            idx_reg = self.lift_ast(node.index)
            reg = self.new_reg()
            self.emit(Opcode.GETTABLE, dest=reg, arg1=obj_reg, arg2=f"[{idx_reg}]")
            return reg

        elif isinstance(node, LocalAssign):
            for i, name in enumerate(node.names):
                val_reg = self.lift_ast(node.values[i]) if i < len(node.values) else None
                self.emit(Opcode.MOVE, dest=name, arg1=val_reg or "nil", comment="local var declaration")
            return None

        elif isinstance(node, Assignment):
            for i, target in enumerate(node.targets):
                val_reg = self.lift_ast(node.values[i]) if i < len(node.values) else None
                target_str = str(target)
                self.emit(Opcode.SETGLOBAL, dest=target_str, arg1=val_reg or "nil")
            return None

        return None
