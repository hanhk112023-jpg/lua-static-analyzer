import unittest
from lua_analyzer.vm_detector import VMDetector, VMSignature

class TestVMDetector(unittest.TestCase):
    def test_detect_luraph(self):
        code = '-- This file was protected using Luraph Obfuscator v15.0 [https://lura.ph/]\nreturn 1'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.LURAPH)
        self.assertTrue(res["has_vm_interpreter"])

    def test_detect_generic_loader(self):
        code = 'loadstring(game:HttpGet("https://example.com/test.lua"))()'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.GENERIC_LOADER)

    def test_detect_dispatcher_loop(self):
        code = 'while state do if state <= 10 then print(1) end end'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertTrue(res["has_dispatcher_loop"])

if __name__ == "__main__":
    unittest.main()
