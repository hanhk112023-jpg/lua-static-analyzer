"""
VM Boundary & Layout Detection Module.
Detects VM interpreter loops, state objects, dispatchers, and virtual registers.
"""

import re
from typing import Dict, List, Any, Optional

class VMLayout:
    def __init__(self):
        self.pc_location: Optional[str] = None
        self.register_location: Optional[str] = None
        self.stack_location: Optional[str] = None
        self.opcode_source: Optional[str] = None
        self.operand_sources: List[str] = []
        self.constant_sources: List[str] = []
        self.prototype_sources: List[str] = []
        self.dispatcher_type: str = "UNKNOWN"
        self.state_variables: List[str] = []
        self.confidence: float = 0.0
        self.evidence: List[Dict[str, Any]] = []

    def add_evidence(self, description: str, confidence: float, source: str = "static_analysis"):
        self.evidence.append({
            "description": description,
            "confidence": confidence,
            "source": source
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pc_location": self.pc_location,
            "register_location": self.register_location,
            "stack_location": self.stack_location,
            "opcode_source": self.opcode_source,
            "operand_sources": self.operand_sources,
            "constant_sources": self.constant_sources,
            "prototype_sources": self.prototype_sources,
            "dispatcher_type": self.dispatcher_type,
            "state_variables": self.state_variables,
            "confidence": self.confidence,
            "evidence": self.evidence
        }

class VMBoundaryDetector:
    def __init__(self, code: str):
        self.code = code

    def detect(self) -> VMLayout:
        layout = VMLayout()

        # 1. Detect Dispatcher & PC
        # Look for while loop with state condition
        while_loop = re.search(
            r'while\s+([a-zA-Z_0-9]+)\s+do\s+if\s+([a-zA-Z_0-9]+)\s*<=\s*([0-9]+)',
            self.code
        )
        if while_loop:
            state_var = while_loop.group(1)
            cond_var = while_loop.group(2)
            layout.dispatcher_type = "BINARY_TREE_DISPATCHER"
            layout.state_variables = [state_var, cond_var]
            layout.pc_location = cond_var
            layout.add_evidence(
                f"Binary decision tree dispatcher loop found: while {state_var} do if {cond_var} <= {while_loop.group(3)}",
                0.90, "dispatcher_search"
            )
            layout.confidence = max(layout.confidence, 0.85)

        # 2. Detect Register Array
        # Pattern: RegArray[dest] = RegArray[src] or similar array mutation
        reg_pattern = re.search(r'\b([a-zA-Z_0-9]+)\[\s*([a-zA-Z_0-9]+)\[[0-9]+\]\s*\]\s*=', self.code)
        if reg_pattern:
            reg_var = reg_pattern.group(1)
            layout.register_location = f"virtual_registers:{reg_var}"
            layout.add_evidence(f"Virtual register array identified: {reg_var}", 0.80, "register_search")

        # 3. Detect Constant Sources
        # Pattern: large array of numbers or strings
        const_tbl = re.search(r'local\s+([a-zA-Z_0-9]+)\s*=\s*\{([0-9,\s\-]{50,})\}', self.code)
        if const_tbl:
            layout.constant_sources.append(const_tbl.group(1))
            layout.add_evidence(f"Numeric constant table detected: {const_tbl.group(1)}", 0.85, "constants")

        # 4. Check for Buffer-based opcode fetching (Luau buffer VM)
        if "buffer.read" in self.code:
            layout.opcode_source = "buffer_stream"
            layout.add_evidence("Bytecode stream fetched via Luau buffer API", 0.90, "buffer_search")

        return layout
