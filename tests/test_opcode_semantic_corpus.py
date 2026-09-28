import unittest
from lua_analyzer.opcode_recovery import OpcodeRecoverer, OpcodeDefinition, SemanticCategory

class TestOpcodeSemanticCorpus(unittest.TestCase):
    def test_infer_call(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(1, "local res = (reg[func])(reg[arg1])")
        self.assertEqual(defn.semantic_category, SemanticCategory.CALL)
        self.assertGreater(defn.confidence, 0.7)

    def test_infer_return(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(2, "return reg[res]")
        self.assertEqual(defn.semantic_category, SemanticCategory.RETURN)
        self.assertEqual(defn.control_flow_effect, "return")

    def test_infer_add(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(3, "reg[dest] = reg[a] + reg[b]")
        self.assertEqual(defn.semantic_category, SemanticCategory.ADD)

    def test_infer_gettable(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(4, "reg[dest] = tbl[idx]")
        self.assertEqual(defn.semantic_category, SemanticCategory.GETTABLE)

    def test_infer_move(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(5, "reg[dest] = reg[src]")
        self.assertEqual(defn.semantic_category, SemanticCategory.MOVE)

    def test_opcode_definition_to_dict(self):
        defn = OpcodeDefinition(42)
        defn.semantic_category = SemanticCategory.LOADK
        defn.reads = ["const_idx"]
        defn.writes = ["reg_A"]
        d = defn.to_dict()
        self.assertEqual(d["opcode_id"], 42)
        self.assertEqual(d["semantic_category"], "LOADK")
        self.assertEqual(d["reads"], ["const_idx"])
        self.assertEqual(d["writes"], ["reg_A"])

    def test_unknown_semantic(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(99, "")
        self.assertEqual(defn.semantic_category, SemanticCategory.UNKNOWN)
        self.assertEqual(defn.confidence, 0.0)

    def test_multiple_opcodes_recovery(self):
        code = """
        if op == 1 then
            reg[a] = reg[b] + reg[c]
        elseif op == 2 then
            return reg[a]
        end
        """
        recoverer = OpcodeRecoverer(code)
        opcodes = recoverer.recover()
        self.assertIn(1, opcodes)
        self.assertIn(2, opcodes)
        self.assertEqual(opcodes[1].semantic_category, SemanticCategory.ADD)
        self.assertEqual(opcodes[2].semantic_category, SemanticCategory.RETURN)

    def test_evidence_recording(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(1, "return 42")
        self.assertTrue(len(defn.evidence) >= 1)

    def test_handler_location_tag(self):
        recoverer = OpcodeRecoverer("")
        defn = recoverer.infer_semantic(7, "reg[a] = reg[b]")
        self.assertEqual(defn.handler_location, "dispatcher_case:7")

if __name__ == "__main__":
    unittest.main()
