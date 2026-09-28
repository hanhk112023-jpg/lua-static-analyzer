"""
Virtual Register Dataflow Analysis Module.
Builds Def-Use chains, tracks reaching definitions and live ranges.
"""

from typing import Dict, List, Set, Any, Optional

class RegisterDef:
    def __init__(self, reg_name: str, instr_idx: int, expr: Any):
        self.reg_name = reg_name
        self.instr_idx = instr_idx
        self.expr = expr
        self.uses: List[int] = []

class DataflowAnalyzer:
    def __init__(self, instructions: List[Any]):
        self.instructions = instructions
        self.definitions: Dict[str, List[RegisterDef]] = {}
        self.use_def_chains: Dict[int, List[RegisterDef]] = {}

    def analyze(self):
        """Builds reaching definitions and def-use chains over sequential instructions."""
        current_defs: Dict[str, RegisterDef] = {}

        for idx, instr in enumerate(self.instructions):
            dest = getattr(instr, "dest", None)
            arg1 = getattr(instr, "arg1", None)
            arg2 = getattr(instr, "arg2", None)

            # Record uses of previous definitions
            for arg in (arg1, arg2):
                if isinstance(arg, str) and arg in current_defs:
                    r_def = current_defs[arg]
                    r_def.uses.append(idx)
                    if idx not in self.use_def_chains:
                        self.use_def_chains[idx] = []
                    self.use_def_chains[idx].append(r_def)

            # Record new definition
            if dest and isinstance(dest, str):
                new_def = RegisterDef(dest, idx, arg1)
                if dest not in self.definitions:
                    self.definitions[dest] = []
                self.definitions[dest].append(new_def)
                current_defs[dest] = new_def

    def to_dict(self) -> Dict[str, Any]:
        return {
            "registers": {
                reg: [
                    {"defined_at": d.instr_idx, "used_at": d.uses, "expr": str(d.expr)}
                    for d in defs
                ]
                for reg, defs in self.definitions.items()
            }
        }
