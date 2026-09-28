"""
Control Flow Graph (CFG) Module.
Analyzes basic blocks, state machines, and control flow flattening.
"""

from typing import List, Dict, Set, Optional, Any

class BasicBlock:
    def __init__(self, block_id: int):
        self.block_id = block_id
        self.instructions: List[Any] = []
        self.predecessors: Set[int] = set()
        self.successors: Set[int] = set()
        self.is_entry = False
        self.is_exit = False

    def add_instruction(self, instr: Any):
        self.instructions.append(instr)

class ControlFlowGraph:
    def __init__(self):
        self.blocks: Dict[int, BasicBlock] = {}
        self.entry_block_id: Optional[int] = None
        self._next_id = 0

    def create_block(self) -> BasicBlock:
        block = BasicBlock(self._next_id)
        self.blocks[self._next_id] = block
        if self.entry_block_id is None:
            self.entry_block_id = self._next_id
            block.is_entry = True
        self._next_id += 1
        return block

    def add_edge(self, from_id: int, to_id: int):
        if from_id in self.blocks and to_id in self.blocks:
            self.blocks[from_id].successors.add(to_id)
            self.blocks[to_id].predecessors.add(from_id)

    def detect_flattening(self) -> Dict[str, Any]:
        """
        Detects control-flow flattening:
        Characterized by a central dispatcher node with high in-degree and out-degree.
        """
        flattened = False
        dispatcher_id = None
        max_edges = 0

        for b_id, block in self.blocks.items():
            in_deg = len(block.predecessors)
            out_deg = len(block.successors)
            if in_deg >= 3 and out_deg >= 3:
                flattened = True
                if in_deg + out_deg > max_edges:
                    max_edges = in_deg + out_deg
                    dispatcher_id = b_id

        return {
            "is_flattened": flattened,
            "dispatcher_block": dispatcher_id,
            "total_blocks": len(self.blocks),
            "edge_density": max_edges
        }
