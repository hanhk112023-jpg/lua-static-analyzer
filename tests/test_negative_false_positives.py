import unittest
from lua_analyzer.vm_detector import VMDetector, VMSignature
from lua_analyzer.payload_extractor import PayloadExtractor

class TestNegativeFalsePositives(unittest.TestCase):
    def test_normal_while_loop_not_vm(self):
        # A normal small while loop shouldn't be classified as Luraph or full VM without evidence
        code = """
        local count = 0
        while count < 10 do
            count = count + 1
            print("Processing item", count)
        end
        """
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.CLEAN_LUA)
        self.assertFalse(res["has_vm_interpreter"])

    def test_normal_if_nested_not_dispatcher(self):
        code = """
        function checkVal(x)
            if x <= 10 then
                return "low"
            else
                return "high"
            end
        end
        """
        detector = VMDetector(code)
        res = detector.detect()
        self.assertFalse(res["has_dispatcher_loop"])
        self.assertEqual(res["identified_type"], VMSignature.CLEAN_LUA)

    def test_normal_image_urls_not_remote_script_payloads(self):
        code = 'local logo = "https://example.com/assets/logo.png"'
        extractor = PayloadExtractor(code)
        res = extractor.extract()
        urls = [u["resolved_value"] for u in res["remote_urls"]]
        # Images are filtered out from payload list
        self.assertNotIn("https://example.com/assets/logo.png", urls)

    def test_normal_math_not_byte_escape_obfuscation(self):
        code = 'local total = 100 + 200 * 3 / 4'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertFalse(res["has_byte_string"])

    def test_normal_print_not_loadstring(self):
        code = 'print("Executing action...")'
        extractor = PayloadExtractor(code)
        res = extractor.extract()
        self.assertEqual(len(res["loadstring_invocations"]), 0)

    def test_clean_table_not_flagged(self):
        code = 'local fruits = {"apple", "banana", "orange"}'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.CLEAN_LUA)

    def test_comments_with_vm_keyword_not_flagged_if_clean(self):
        code = '-- Note: this is not a Luraph script\nprint("Hello")'
        detector = VMDetector(code)
        res = detector.detect()
        # Even if watermark found in comment, confidence reflects watermark only
        self.assertFalse(res["has_dispatcher_loop"])

    def test_short_hex_not_dense_obfuscation(self):
        code = 'local s = "\\x41\\x42"'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertFalse(res["has_byte_string"])

    def test_simple_for_loop_clean(self):
        code = 'for i = 1, 10 do print(i) end'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.CLEAN_LUA)

    def test_normal_concatenation_clean(self):
        code = 'local name = "User" .. "123"'
        detector = VMDetector(code)
        res = detector.detect()
        self.assertEqual(res["identified_type"], VMSignature.CLEAN_LUA)

if __name__ == "__main__":
    unittest.main()
