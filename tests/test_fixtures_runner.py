import unittest
import os
import tempfile
import shutil
from lua_analyzer import LuaStaticAnalyzer

class TestFixturesRunner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_all_fixtures_regression(self):
        """Runs the entire analysis and devirtualization pipeline across all regression fixtures."""
        fixture_count = 0
        for root, _, files in os.walk(self.fixtures_dir):
            for f in files:
                if f.endswith(".lua"):
                    fixture_count += 1
                    full_path = os.path.join(root, f)
                    out_dir = os.path.join(self.temp_dir, f"out_{fixture_count}")
                    os.makedirs(out_dir, exist_ok=True)

                    analyzer = LuaStaticAnalyzer(full_path, out_dir)
                    cleaned, report, ir = analyzer.run_pipeline()

                    self.assertTrue(os.path.isfile(cleaned))
                    self.assertTrue(os.path.isfile(report))
                    self.assertTrue(os.path.isfile(ir))

                    # Verify deterministic rerun: second run should produce identical bytes
                    out_dir2 = os.path.join(self.temp_dir, f"out_{fixture_count}_deterministic")
                    os.makedirs(out_dir2, exist_ok=True)
                    analyzer2 = LuaStaticAnalyzer(full_path, out_dir2)
                    cleaned2, _, _ = analyzer2.run_pipeline()

                    with open(cleaned, "rb") as f1, open(cleaned2, "rb") as f2:
                        self.assertEqual(f1.read(), f2.read(), f"Determinism violation on fixture {f}")

        self.assertGreaterEqual(fixture_count, 12)

if __name__ == "__main__":
    unittest.main()
