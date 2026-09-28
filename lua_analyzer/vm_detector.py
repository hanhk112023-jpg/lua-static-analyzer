"""
VM & Obfuscation Detector Module.
Identifies obfuscator signatures, VM interpreters, and control flow flattening.
"""

import re
from typing import Dict, Any, List

class VMSignature:
    LURAPH = "Luraph Obfuscator (v11-v15 Bytecode VM)"
    IRONBREW = "IronBrew / Luraph VM Derivative"
    MOONSEC = "MoonSec Obfuscator"
    PSU = "PSU Obfuscator"
    BYTE_ESCAPE = "Dense Byte-Escape / Hex Obfuscation"
    FLATTENED_CFG = "Control Flow Flattening (Dispatcher Loop)"
    GENERIC_LOADER = "Generic Remote Script Loader"
    CLEAN_LUA = "Standard Unobfuscated Lua Script"

class VMDetector:
    def __init__(self, code: str):
        self.code = code

    def detect(self) -> Dict[str, Any]:
        results = {
            "identified_type": VMSignature.CLEAN_LUA,
            "confidence": 0.0,
            "characteristics": [],
            "has_vm_interpreter": False,
            "has_dispatcher_loop": False,
            "has_byte_string": False
        }

        # 1. Direct Watermarks
        if "Luraph" in self.code or "lura.ph" in self.code or "LPH:" in self.code:
            results["identified_type"] = VMSignature.LURAPH
            results["confidence"] = 0.99
            results["characteristics"].append("Found Luraph watermark/signature string")
            results["has_vm_interpreter"] = True

        elif "IronBrew" in self.code or "IB2" in self.code:
            results["identified_type"] = VMSignature.IRONBREW
            results["confidence"] = 0.95
            results["characteristics"].append("Found IronBrew watermark/signature")
            results["has_vm_interpreter"] = True

        elif "Moonsec" in self.code or "MoonSec" in self.code:
            results["identified_type"] = VMSignature.MOONSEC
            results["confidence"] = 0.95
            results["characteristics"].append("Found MoonSec signature")
            results["has_vm_interpreter"] = True

        elif "PSU Obfuscator" in self.code:
            results["identified_type"] = VMSignature.PSU
            results["confidence"] = 0.95
            results["characteristics"].append("Found PSU signature")
            results["has_vm_interpreter"] = True

        # 2. Heuristic VM Detection (dispatcher loop + large opcode table)
        dispatcher_pattern = re.compile(
            r'while\s+[a-zA-Z_0-9]+\s+do\s+if\s+[a-zA-Z_0-9]+\s*<=\s*[0-9]+',
            re.IGNORECASE
        )
        if dispatcher_pattern.search(self.code):
            results["has_dispatcher_loop"] = True
            results["characteristics"].append("Detected nested binary search opcode dispatcher")
            if results["identified_type"] == VMSignature.CLEAN_LUA:
                results["identified_type"] = VMSignature.FLATTENED_CFG
                results["confidence"] = 0.85
                results["has_vm_interpreter"] = True

        # 3. Dense Byte / Hex Escapes
        escape_count = len(re.findall(r'\\(?:[0-9]{2,3}|x[0-9a-fA-F]{2})', self.code))
        if escape_count > 20:
            results["has_byte_string"] = True
            results["characteristics"].append(f"Found {escape_count} escaped byte characters")
            if results["identified_type"] == VMSignature.CLEAN_LUA:
                results["identified_type"] = VMSignature.BYTE_ESCAPE
                results["confidence"] = 0.80

        # 4. Loader Pattern
        if re.search(r'loadstring\s*\(\s*(?:game|self|Workspace)[\s:]+(?:HttpGet|HttpGetAsync)', self.code, re.IGNORECASE):
            results["characteristics"].append("Detected remote HttpGet loader pattern")
            if results["identified_type"] == VMSignature.CLEAN_LUA:
                results["identified_type"] = VMSignature.GENERIC_LOADER
                results["confidence"] = 0.90

        return results
