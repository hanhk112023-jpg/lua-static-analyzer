"""
Opcode Recovery & Semantic Inference Module.
Recovers VM instruction opcodes, operand encodings, and infers high-level semantics.
"""

import re
from typing import Dict, List, Any, Optional

class SemanticCategory:
    LOADK = "LOADK"
    MOVE = "MOVE"
    GETGLOBAL = "GETGLOBAL"
    SETGLOBAL = "SETGLOBAL"
    GETTABLE = "GETTABLE"
    SETTABLE = "SETTABLE"
    CALL = "CALL"
    RETURN = "RETURN"
    JMP = "JMP"
    TEST = "TEST"
    TESTSET = "TESTSET"
    CLOSURE = "CLOSURE"
    GETUPVAL = "GETUPVAL"
    SETUPVAL = "SETUPVAL"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    POW = "POW"
    EQ = "EQ"
    LT = "LT"
    LE = "LE"
    UNKNOWN = "UNKNOWN"

class OpcodeDefinition:
    def __init__(self, opcode_id: int):
        self.opcode_id = opcode_id
        self.handler_location: str = "unknown"
        self.operands: List[str] = []
        self.reads: List[str] = []
        self.writes: List[str] = []
        self.stack_effect: int = 0
        self.register_effect: str = "none"
        self.control_flow_effect: str = "fallthrough"
        self.constant_access: bool = False
        self.semantic_category: str = SemanticCategory.UNKNOWN
        self.confidence: float = 0.0
        self.evidence: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opcode_id": self.opcode_id,
            "semantic_category": self.semantic_category,
            "handler_location": self.handler_location,
            "operands": self.operands,
            "reads": self.reads,
            "writes": self.writes,
            "constant_access": self.constant_access,
            "confidence": self.confidence,
            "evidence": self.evidence
        }

class OpcodeRecoverer:
    def __init__(self, code: str):
        self.code = code
        self.opcodes: Dict[int, OpcodeDefinition] = {}

    def recover(self) -> Dict[int, OpcodeDefinition]:
        # Scan for handler assignments or cases:
        # e.g. if op == 1 or case 1 or handler table
        case_pattern = re.compile(
            r'(?:elseif|if)\s+([a-zA-Z_0-9]+)\s*(?:==|<=)\s*([0-9]+)\s+then(.*?)(?=(?:elseif|else|end))',
            re.DOTALL
        )
        for m in case_pattern.finditer(self.code):
            op_num = int(m.group(2))
            body = m.group(3)
            defn = self.infer_semantic(op_num, body)
            self.opcodes[op_num] = defn

        return self.opcodes

    def infer_semantic(self, op_num: int, body: str) -> OpcodeDefinition:
        defn = OpcodeDefinition(op_num)
        defn.handler_location = f"dispatcher_case:{op_num}"

        # Heuristic 1: Call
        if re.search(r'\([a-zA-Z_0-9]+\[[a-zA-Z_0-9]+\]\)\(', body) or "pcall" in body:
            defn.semantic_category = SemanticCategory.CALL
            defn.confidence = 0.85
            defn.evidence.append("Contains function invocation on virtual register")
            defn.writes.append("virtual_return_register")

        # Heuristic 2: Return
        elif "return " in body and not any(k in body for k in ("function", "pcall")):
            defn.semantic_category = SemanticCategory.RETURN
            defn.confidence = 0.90
            defn.evidence.append("Direct return statement in handler")
            defn.control_flow_effect = "return"

        # Heuristic 3: Arithmetic Add
        elif "+" in body and "=" in body:
            defn.semantic_category = SemanticCategory.ADD
            defn.confidence = 0.75
            defn.evidence.append("Addition assignment detected in handler")

        # Heuristic 4: Move / Register Assignment (reg[a] = reg[b])
        elif re.search(r'([a-zA-Z_0-9]+)\[[^\]]+\]\s*=\s*\1\[[^\]]+\]', body):
            defn.semantic_category = SemanticCategory.MOVE
            defn.confidence = 0.80
            defn.evidence.append("Register to register copy detected")

        # Heuristic 5: Table Get / Load Constant
        elif re.search(r'\b([a-zA-Z_0-9]+)\[\s*([a-zA-Z_0-9]+)\s*\]', body):
            defn.semantic_category = SemanticCategory.GETTABLE
            defn.confidence = 0.70
            defn.evidence.append("Table indexing detected")

        # Heuristic 6: Generic Move / Assignment
        elif "=" in body:
            defn.semantic_category = SemanticCategory.MOVE
            defn.confidence = 0.60
            defn.evidence.append("Register assignment detected")

        return defn
