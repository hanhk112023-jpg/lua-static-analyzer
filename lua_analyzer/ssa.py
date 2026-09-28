"""
Static Single Assignment (SSA) & Sparse Conditional Constant Propagation (SCCP) Module.
Versioned registers, Phi nodes, lattice-based constant propagation and branch pruning.
"""

from typing import Dict, List, Set, Any, Optional, Tuple

class LatticeValue:
    TOP = "TOP"         # Uninitialized
    BOTTOM = "BOTTOM"   # Non-constant / Overdefined

class SSAVar:
    def __init__(self, base_name: str, version: int):
        self.base_name = base_name
        self.version = version

    def __str__(self) -> str:
        return f"{self.base_name}_{self.version}"

class PhiNode:
    def __init__(self, dest: SSAVar, incoming: List[SSAVar]):
        self.dest = dest
        self.incoming = incoming

    def __str__(self) -> str:
        return f"{self.dest} = Phi({', '.join(str(v) for v in self.incoming)})"

class SCCP:
    """
    Sparse Conditional Constant Propagation engine.
    Computes static constants and prunes dead branches in linear or CFG code.
    """

    def __init__(self):
        self.lat_values: Dict[str, Any] = {} # var_name -> (LatticeValue.TOP | LatticeValue.BOTTOM | concrete_val)
        self.eliminated_branches: List[Dict[str, Any]] = []

    def meet(self, v1: Any, v2: Any) -> Any:
        if v1 == LatticeValue.TOP:
            return v2
        if v2 == LatticeValue.TOP:
            return v1
        if v1 == v2:
            return v1
        return LatticeValue.BOTTOM

    def propagate_linear(self, instructions: List[Any]) -> List[Any]:
        """Performs SCCP constant folding over IR instructions with provenance tracking."""
        simplified = []

        for idx, instr in enumerate(instructions):
            dest = getattr(instr, "dest", None)
            op = getattr(instr, "op", None)
            arg1 = getattr(instr, "arg1", None)
            arg2 = getattr(instr, "arg2", None)

            # Check if arg1 or arg2 are known constants in lattice
            folded_arg1 = self.lat_values.get(arg1, arg1) if isinstance(arg1, str) else arg1
            folded_arg2 = self.lat_values.get(arg2, arg2) if isinstance(arg2, str) else arg2

            if op == "LOADK" and dest:
                # Direct constant assignment
                self.lat_values[dest] = arg1
                simplified.append(instr)

            elif op == "MOVE" and dest:
                val = self.lat_values.get(str(arg1), LatticeValue.BOTTOM) if arg1 is not None else LatticeValue.BOTTOM
                self.lat_values[dest] = val
                simplified.append(instr)

            elif op == "JMP_IF_FALSE":
                cond_val = self.lat_values.get(str(arg1), LatticeValue.BOTTOM) if arg1 is not None else LatticeValue.BOTTOM
                if cond_val is False or cond_val == 0:
                    # Unconditionally taken jump
                    self.eliminated_branches.append({
                        "instr_idx": idx,
                        "branch_type": "JMP_IF_FALSE",
                        "condition_evaluated_to": cond_val,
                        "provenance": "SCCP constant condition folding"
                    })
                    # Transform to unconditional JMP
                    setattr(instr, "op", "JMP")
                elif cond_val is True or (isinstance(cond_val, (int, str)) and cond_val != 0):
                    # Never taken jump -> dead instruction
                    self.eliminated_branches.append({
                        "instr_idx": idx,
                        "branch_type": "JMP_IF_FALSE",
                        "condition_evaluated_to": cond_val,
                        "provenance": "Pruned dead branch"
                    })
                    continue # Do not include in simplified instructions
                simplified.append(instr)

            else:
                simplified.append(instr)

        return simplified
