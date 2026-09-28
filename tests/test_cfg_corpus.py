import unittest
from lua_analyzer.cfg import ControlFlowGraph, BasicBlock

class TestCFGCorpus(unittest.TestCase):
    def test_block_creation(self):
        cfg = ControlFlowGraph()
        b0 = cfg.create_block()
        b1 = cfg.create_block()
        self.assertEqual(b0.block_id, 0)
        self.assertEqual(b1.block_id, 1)
        self.assertTrue(b0.is_entry)
        self.assertFalse(b1.is_entry)

    def test_edge_addition(self):
        cfg = ControlFlowGraph()
        b0 = cfg.create_block()
        b1 = cfg.create_block()
        cfg.add_edge(b0.block_id, b1.block_id)
        self.assertIn(b1.block_id, b0.successors)
        self.assertIn(b0.block_id, b1.predecessors)

    def test_instruction_addition(self):
        b = BasicBlock(0)
        b.add_instruction("LOADK R1, 100")
        self.assertEqual(len(b.instructions), 1)

    def test_natural_loop_detection(self):
        cfg = ControlFlowGraph()
        b0 = cfg.create_block()
        b1 = cfg.create_block()
        cfg.add_edge(b0.block_id, b1.block_id)
        cfg.add_edge(b1.block_id, b0.block_id) # back-edge
        loops = cfg.detect_loops()
        self.assertEqual(len(loops), 1)
        self.assertEqual(loops[0]["header"], 0)
        self.assertEqual(loops[0]["tail"], 1)

    def test_flattening_detection(self):
        cfg = ControlFlowGraph()
        # Create dispatcher with high in/out degree
        disp = cfg.create_block()
        for _ in range(4):
            b = cfg.create_block()
            cfg.add_edge(disp.block_id, b.block_id)
            cfg.add_edge(b.block_id, disp.block_id)
        res = cfg.detect_flattening()
        self.assertTrue(res["is_flattened"])
        self.assertEqual(res["dispatcher_block"], disp.block_id)

    def test_clean_cfg_no_flattening(self):
        cfg = ControlFlowGraph()
        b0 = cfg.create_block()
        b1 = cfg.create_block()
        cfg.add_edge(b0.block_id, b1.block_id)
        res = cfg.detect_flattening()
        self.assertFalse(res["is_flattened"])

    def test_irreducible_normalization(self):
        cfg = ControlFlowGraph()
        b0 = cfg.create_block()
        b1 = cfg.create_block()
        b2 = cfg.create_block()
        cfg.add_edge(b0.block_id, b1.block_id)
        cfg.add_edge(b0.block_id, b2.block_id)
        cfg.add_edge(b1.block_id, b2.block_id)
        cfg.add_edge(b2.block_id, b1.block_id)
        normalized = cfg.normalize_irreducible()
        self.assertTrue(normalized)

    def test_block_to_dict(self):
        b = BasicBlock(5)
        b.branch_condition = "R1 == 0"
        d = b.to_dict()
        self.assertEqual(d["block_id"], 5)
        self.assertEqual(d["branch_condition"], "R1 == 0")

    def test_cfg_to_dict(self):
        cfg = ControlFlowGraph()
        cfg.create_block()
        cfg.create_block()
        d = cfg.to_dict()
        self.assertEqual(d["total_blocks"], 2)
        self.assertEqual(d["entry_block_id"], 0)

    def test_empty_cfg(self):
        cfg = ControlFlowGraph()
        d = cfg.to_dict()
        self.assertEqual(d["total_blocks"], 0)
        self.assertIsNone(d["entry_block_id"])

if __name__ == "__main__":
    unittest.main()
