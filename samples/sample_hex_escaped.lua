-- Sample 2: Byte & Hex Escaped Strings + Concatenation
local domain = "\104\116\116\112\115\058\047\047" .. "\x61\x70\x69\x2e\x65\x78\x61\x6d\x70\x6c\x65\x2e\x63\x6f\x6d"
local endpoint = "/v1" .. "/auth" .. "/session"
local full_url = domain .. endpoint

print(full_url)
