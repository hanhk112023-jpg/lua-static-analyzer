import unittest
import os
import shutil
import tempfile
from lua_analyzer.analyzer import LuaStaticAnalyzer

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.samples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "samples"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_on_sample_loader(self):
        sample_path = os.path.join(self.samples_dir, "sample_loader.lua")
        analyzer = LuaStaticAnalyzer(sample_path, self.temp_dir)
        cleaned, report, ir = analyzer.run_pipeline()

        self.assertTrue(os.path.isfile(cleaned))
        self.assertTrue(os.path.isfile(report))
        self.assertTrue(os.path.isfile(ir))

        with open(report, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("https://example.invalid/file.lua", content)

    def test_run_on_sample_hex(self):
        sample_path = os.path.join(self.samples_dir, "sample_hex_escaped.lua")
        analyzer = LuaStaticAnalyzer(sample_path, self.temp_dir)
        cleaned, report, ir = analyzer.run_pipeline()

        with open(cleaned, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertIn("https://api.example.com", code)

    def test_run_on_sample_table(self):
        sample_path = os.path.join(self.samples_dir, "sample_table_mapped.lua")
        analyzer = LuaStaticAnalyzer(sample_path, self.temp_dir)
        cleaned, report, ir = analyzer.run_pipeline()

        with open(cleaned, "r", encoding="utf-8") as f:
            code = f.read()
            self.assertIn("Security Audit", code)
            self.assertIn("30", code)

if __name__ == "__main__":
    unittest.main()
