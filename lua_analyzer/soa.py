"""
Structure-of-Arrays (SoA) Recovery Module.
Identifies VM instruction layouts:
opcode[], operandA[], operandB[], operandC[], constant[], prototype[]
Variable-name agnostic; discovers array sets via shared index expressions.
"""

import re
from typing import Dict, List, Set, Any, Optional

class SoAMapping:
    def __init__(self):
        self.arrays: Dict[str, str] = {}  # array_name -> logical_role (e.g. "opcodes", "operands_a")
        self.shared_index_vars: Set[str] = set()
        self.field_permutations: Dict[str, str] = {} # logical_field -> physical_field
        self.index_offsets: Dict[str, int] = {} # array_name -> offset relative to pc
        self.confidence: float = 0.0
        self.evidence: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arrays": self.arrays,
            "shared_index_vars": list(self.shared_index_vars),
            "field_permutations": self.field_permutations,
            "index_offsets": self.index_offsets,
            "confidence": self.confidence,
            "evidence": self.evidence
        }

class SoAAnalyzer:
    def __init__(self, code: str):
        self.code = code

    def analyze(self) -> SoAMapping:
        mapping = SoAMapping()

        # Find array indexing patterns: ArrayVar[IndexVar (+/- offset)?]
        access_pattern = re.compile(
            r'\b([a-zA-Z_0-9]+)\s*\[\s*([a-zA-Z_0-9]+)(?:\s*([\+\-])\s*([0-9]+))?\s*\]'
        )

        # Map index_var -> set of (array_var, offset)
        index_usage: Dict[str, Set[tuple]] = {}
        for m in access_pattern.finditer(self.code):
            arr_var = m.group(1)
            idx_var = m.group(2)
            op = m.group(3)
            offset_val = int(m.group(4)) if m.group(4) else 0
            offset = offset_val if op != "-" else -offset_val

            # Skip common non-VM keywords / tables
            if arr_var in ("string", "table", "math", "bit32", "buffer", "os", "game"):
                continue

            if idx_var not in index_usage:
                index_usage[idx_var] = set()
            index_usage[idx_var].add((arr_var, offset))

        # Look for index variables that index 3 or more distinct arrays in the code (candidate PC)
        candidate_pc = None
        max_arrays = 0
        for idx_var, accesses in index_usage.items():
            distinct_arrays = {arr for arr, _ in accesses}
            if len(distinct_arrays) >= 3 and len(distinct_arrays) > max_arrays:
                max_arrays = len(distinct_arrays)
                candidate_pc = idx_var

        if candidate_pc:
            mapping.shared_index_vars.add(candidate_pc)
            mapping.evidence.append(f"Identified virtual PC index variable '{candidate_pc}' accessing {max_arrays} correlated arrays")
            mapping.confidence = min(0.95, 0.4 + (max_arrays * 0.1))

            # Categorize the arrays based on access patterns / offsets
            sorted_accesses = sorted(list(index_usage[candidate_pc]), key=lambda x: x[1])
            roles = ["opcode", "operand_A", "operand_B", "operand_C", "operand_D"]
            for i, (arr_name, offset) in enumerate(sorted_accesses):
                role = roles[i] if i < len(roles) else f"operand_extra_{i}"
                mapping.arrays[arr_name] = role
                mapping.index_offsets[arr_name] = offset
                mapping.field_permutations[role] = arr_name

        return mapping
