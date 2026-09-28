-- Sample 3: Table String Array Mapping & Constant Arithmetic
local StrTable = {"Security", "Audit", "ZeroExecution", "Verified"}
local status = StrTable[1] .. " " .. StrTable[2]
local code = 10 + 20
local key = StrTable[3]

print(status, code, key)
