import unittest
from lua_analyzer.dispatcher import DispatcherDevirtualizer, DispatcherModel

class TestDispatcherCorpus(unittest.TestCase):
    def test_state_variable_detection(self):
        code = 'while my_state do if my_state == 1 then end end'
        d = DispatcherDevirtualizer(code)
        m = d.analyze_dispatcher()
        self.assertIsNotNone(m)
        assert m is not None
        self.assertEqual(m.state_variable, "my_state")

    def test_transition_rules_linear(self):
        code = 'while state do state = 1; state = 2; state = 3; state = nil; end'
        d = DispatcherDevirtualizer(code)
        m = d.analyze_dispatcher()
        assert m is not None
        self.assertIn(1, m.transition_rules)
        self.assertEqual(m.transition_rules[1], 2)
        self.assertEqual(m.transition_rules[2], 3)

    def test_unrolling_sequence(self):
        code = 'while state do state = 1; state = 2; state = 3; state = nil; end'
        d = DispatcherDevirtualizer(code)
        d.analyze_dispatcher()
        seq = d.unroll_linear_sequence()
        self.assertEqual(seq, [1, 2, 3])

    def test_termination_handling(self):
        code = 'while state do state = 1; state = nil; end'
        d = DispatcherDevirtualizer(code)
        d.analyze_dispatcher()
        seq = d.unroll_linear_sequence()
        self.assertEqual(seq, [1])

    def test_cycle_detection(self):
        # A cyclic transition: 1 -> 2 -> 1
        model = DispatcherModel(state_variable="state")
        model.transition_rules = {1: 2, 2: 1}
        d = DispatcherDevirtualizer("")
        d.model = model
        seq = d.unroll_linear_sequence()
        # Should terminate cleanly without hanging
        self.assertTrue(len(seq) <= 2)

    def test_max_unroll_limit(self):
        model = DispatcherModel(state_variable="state")
        # Long sequence: 1 -> 2 -> 3 ...
        model.transition_rules = {i: i + 1 for i in range(1, 200)}
        d = DispatcherDevirtualizer("")
        d.model = model
        seq = d.unroll_linear_sequence(max_unroll=50)
        self.assertEqual(len(seq), 50)

    def test_empty_dispatcher(self):
        code = 'print("no dispatcher")'
        d = DispatcherDevirtualizer(code)
        m = d.analyze_dispatcher()
        self.assertIsNone(m)

    def test_dispatcher_model_dict(self):
        m = DispatcherModel(state_variable="pc", dispatcher_type="SWITCH")
        m.transition_rules = {10: 20}
        d_dict = m.to_dict()
        self.assertEqual(d_dict["state_variable"], "pc")
        self.assertEqual(d_dict["dispatcher_type"], "SWITCH")
        self.assertEqual(d_dict["transitions"], {10: 20})

    def test_confidence_metric(self):
        code = 'while state do state = 1; state = 2; end'
        d = DispatcherDevirtualizer(code)
        m = d.analyze_dispatcher()
        assert m is not None
        self.assertGreater(m.confidence, 0.5)

    def test_branch_jump_state(self):
        code = 'while state do state = 10; state = 20; state = -1; end'
        d = DispatcherDevirtualizer(code)
        m = d.analyze_dispatcher()
        assert m is not None
        self.assertIn(10, m.transition_rules)
        self.assertEqual(m.transition_rules[10], 20)

if __name__ == "__main__":
    unittest.main()
