import unittest
import os
import tempfile
import shutil
import socket
import urllib.request
import http.client
import subprocess
from unittest.mock import patch

from lua_analyzer import LuaStaticAnalyzer

class TestZeroExecutionSandbox(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.samples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "samples"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyzer_with_network_and_exec_blocked(self):
        """
        Verify that analyzer completes without making network calls or running subcommands,
        even when analyzing malicious payloads and loader files.
        """
        def blocked_call(*args, **kwargs):
            raise AssertionError("Zero-Execution Violation: Attempted external execution or network access!")

        # Monkeypatch network and process creation
        with patch.object(socket, 'socket', blocked_call), \
             patch.object(urllib.request, 'urlopen', blocked_call), \
             patch.object(http.client.HTTPConnection, 'connect', blocked_call), \
             patch.object(subprocess, 'Popen', blocked_call), \
             patch.object(os, 'system', blocked_call):

            for sample_file in os.listdir(self.samples_dir):
                if sample_file.endswith(".lua"):
                    full_sample_path = os.path.join(self.samples_dir, sample_file)
                    analyzer = LuaStaticAnalyzer(full_sample_path, self.temp_dir)
                    cleaned, report, ir = analyzer.run_pipeline()

                    self.assertTrue(os.path.isfile(cleaned))
                    self.assertTrue(os.path.isfile(report))
                    self.assertTrue(os.path.isfile(ir))

if __name__ == "__main__":
    unittest.main()
