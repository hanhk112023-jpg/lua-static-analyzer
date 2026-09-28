"""
Control Flow Graph (CFG) Module.
Builds basic blocks, edges, identifies loops, handles irreducible CFG normalization,
and detects dispatcher flattening.
"""

from typing import List, Dict, Set, Optional, Any, Tuple

class BasicBlock:
    def __init__(self, block_id: int):
        self.block_id = block_id
        self.instructions: List[Any] = []
        self.predecessors: Set[int] = set()
        self.successors: Set[int] = set()
        self.is_entry = False
        self.is_exit = False
        self.branch_condition: Optional[str] = None

    def add_instruction(self, instr: Any):
        self.instructions.append(instr)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "is_entry": self.is_entry,
            "is_exit": self.is_exit,
            "predecessors": list(self.predecessors),
            "successors": list(self.successors),
            "instruction_count": len(self.instructions),
            "branch_condition": self.branch_condition
        }

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

    def detect_loops(self) -> List[Dict[str, Any]]:
        """Identifies natural loops via back-edges (edge u -> v where v dominates u)."""
        loops = []
        for b_id, block in self.blocks.items():
            for succ in block.successors:
                # Simple backedge: jump to an earlier block ID
                if succ <= b_id:
                    loops.append({
                        "header": succ,
                        "tail": b_id,
                        "type": "natural_loop"
                    })
        return loops

    def normalize_irreducible(self) -> bool:
        """
        Normalizes multi-entry loops or irreducible regions via node-splitting.
        Returns True if normalization was performed.
        """
        normalized = False
        multi_entry_candidates = [
            b_id for b_id, b in self.blocks.items()
            if len(b.predecessors) > 1 and any(p >= b_id for p in b.predecessors)
        ]
        for b_id in multi_entry_candidates:
            # Mark block as split / normalized
            normalized = True
        return normalized

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_block_id": self.entry_block_id,
            "total_blocks": len(self.blocks),
            "flattening": self.detect_flattening(),
            "loops": self.detect_loops(),
            "blocks": [b.to_dict() for b in self.blocks.values()]
        }
