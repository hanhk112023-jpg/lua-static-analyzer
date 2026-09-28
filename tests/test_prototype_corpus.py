import unittest
from lua_analyzer.prototype import Prototype, PrototypeGraph, PrototypeRole

class TestPrototypeCorpus(unittest.TestCase):
    def test_prototype_creation(self):
        p = Prototype(prototype_id=0)
        self.assertEqual(p.prototype_id, 0)
        self.assertIsNone(p.parent_id)

    def test_child_linking(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        p1 = Prototype(prototype_id=1, parent_id=0)
        graph.add_prototype(p0)
        graph.add_prototype(p1)
        self.assertIn(1, p0.child_prototypes)

    def test_bootstrap_role(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        graph.add_prototype(p0)
        graph.classify_roles()
        self.assertEqual(p0.role, PrototypeRole.BOOTSTRAP)

    def test_decoder_role(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        p1 = Prototype(prototype_id=1, parent_id=0)
        p1.instructions = ["bit32.bxor(a, b)"]
        graph.add_prototype(p0)
        graph.add_prototype(p1)
        graph.classify_roles()
        self.assertEqual(p1.role, PrototypeRole.DECODER)

    def test_application_payload_role(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        p1 = Prototype(prototype_id=1, parent_id=0)
        p1.instructions = [f"inst_{i}" for i in range(60)]
        graph.add_prototype(p0)
        graph.add_prototype(p1)
        graph.classify_roles()
        self.assertEqual(p1.role, PrototypeRole.APPLICATION_PAYLOAD)

    def test_vm_runtime_role(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        p1 = Prototype(prototype_id=1, parent_id=0)
        p1.instructions = ["move R1, R2"]
        graph.add_prototype(p0)
        graph.add_prototype(p1)
        graph.classify_roles()
        self.assertEqual(p1.role, PrototypeRole.VM_RUNTIME)

    def test_parameters_and_upvalues(self):
        p = Prototype(prototype_id=5)
        p.parameters = ["arg1", "arg2"]
        p.upvalues = ["up1"]
        d = p.to_dict()
        self.assertEqual(d["parameters"], ["arg1", "arg2"])
        self.assertEqual(d["upvalues"], ["up1"])

    def test_graph_serialization(self):
        graph = PrototypeGraph()
        p0 = Prototype(prototype_id=0)
        graph.add_prototype(p0)
        d = graph.to_dict()
        self.assertEqual(d["total_prototypes"], 1)
        self.assertEqual(d["root_id"], 0)

    def test_constant_pool_in_prototype(self):
        from lua_analyzer.constants import ConstExpr
        p = Prototype(prototype_id=2)
        idx = p.constants.add(ConstExpr("LITERAL", [123]))
        self.assertEqual(idx, 0)
        self.assertEqual(p.to_dict()["constant_count"], 1)

    def test_confidence_and_evidence(self):
        p = Prototype(prototype_id=3)
        p.evidence.append("Found signature")
        self.assertEqual(len(p.to_dict()["evidence"]), 1)

if __name__ == "__main__":
    unittest.main()
