"""
Opcode Analyzer Module.
Statically analyzes VM dispatcher trees, handler mappings, and state transitions.
"""

import re
from typing import Dict, List, Any

class OpcodeAnalyzer:
    def __init__(self, code: str):
        self.code = code

    def analyze(self) -> Dict[str, Any]:
        results = {
            "dispatcher_detected": False,
            "comparison_thresholds": [],
            "identified_handlers": [],
            "estimated_opcodes_count": 0
        }

        # Scan for binary search branching: if O <= 134 then ... elseif O <= 135
        cond_pattern = re.compile(r'if\s+([a-zA-Z_0-9]+)\s*<=\s*([0-9]+)\s+then', re.IGNORECASE)
        thresholds = []
        for m in cond_pattern.finditer(self.code):
            var_name = m.group(1)
            val = int(m.group(2))
            thresholds.append((var_name, val))

        if thresholds:
            results["dispatcher_detected"] = True
            results["comparison_thresholds"] = sorted(list(set(t[1] for t in thresholds)))
            results["estimated_opcodes_count"] = len(results["comparison_thresholds"]) + 1

        # Scan for named handler mappings: e.g. n4=function(C,e,O...)
        handler_pattern = re.compile(r'([a-zA-Z_0-9]+)\s*=\s*function\s*\(([^)]*)\)')
        for m in handler_pattern.finditer(self.code):
            name = m.group(1)
            args = [a.strip() for a in m.group(2).split(",") if a.strip()]
            if len(args) >= 3: # Typical VM instruction handler receives context, env, pc, etc.
                results["identified_handlers"].append({"name": name, "arg_count": len(args)})

        return results
