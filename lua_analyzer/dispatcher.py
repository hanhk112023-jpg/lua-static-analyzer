"""
Dispatcher Devirtualization Module.
Models and unrolls state machine dispatchers, binary decision trees, and flattened control flows.
Transforms VM opcode dispatch sequences into linearized logical blocks.
"""

import re
from typing import Dict, List, Any, Optional

class DispatcherModel:
    def __init__(self, state_variable: str, dispatcher_type: str = "BINARY_TREE"):
        self.state_variable = state_variable
        self.dispatcher_type = dispatcher_type
        self.dispatch_blocks: List[int] = []
        self.transition_rules: Dict[int, int] = {} # current_state -> next_state
        self.handler_mapping: Dict[int, str] = {} # state -> handler_snippet
        self.confidence: float = 0.80

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_variable": self.state_variable,
            "dispatcher_type": self.dispatcher_type,
            "dispatch_blocks_count": len(self.dispatch_blocks),
            "transition_rules_count": len(self.transition_rules),
            "transitions": self.transition_rules,
            "confidence": self.confidence
        }

class DispatcherDevirtualizer:
    def __init__(self, code: str):
        self.code = code
        self.model: Optional[DispatcherModel] = None

    def analyze_dispatcher(self) -> Optional[DispatcherModel]:
        # Detect state variable in while loop
        loop_match = re.search(r'while\s+([a-zA-Z_0-9]+)\s+do', self.code)
        if not loop_match:
            return None

        state_var = loop_match.group(1)
        model = DispatcherModel(state_variable=state_var)

        # Detect state transitions: state = N
        trans_pattern = re.compile(
            r'state\s*=\s*([0-9]+|nil)'
        )
        states_found = []
        for m in trans_pattern.finditer(self.code):
            val = m.group(1)
            states_found.append(int(val) if val != "nil" else -1)

        for i in range(len(states_found) - 1):
            curr_s = states_found[i]
            next_s = states_found[i + 1]
            if curr_s != -1:
                model.transition_rules[curr_s] = next_s

        self.model = model
        return model

    def unroll_linear_sequence(self, max_unroll: int = 1000) -> List[int]:
        """Unrolls the state machine sequence into linear execution order."""
        if not self.model or not self.model.transition_rules:
            return []

        seq = []
        curr = min(self.model.transition_rules.keys()) if self.model.transition_rules else 1
        visited = set()

        while curr in self.model.transition_rules and len(seq) < max_unroll:
            if curr in visited:
                break # Loop cycle detected
            visited.add(curr)
            seq.append(curr)
            curr = self.model.transition_rules[curr]
            if curr == -1: # nil / terminate
                break

        return seq
