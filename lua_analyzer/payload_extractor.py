"""
Payload Extractor Module.
Statically analyzes untrusted Lua source code to locate and extract:
- URLs in HttpGet / HttpGetAsync / request calls
- Loadstring / dynamic execution wrappers
- Embedded byte / Base64 payload data
NEVER executes any code or initiates network communication.
"""

import re
import base64
from typing import Dict, List, Any

class PayloadExtractor:
    def __init__(self, code: str):
        self.code = code

    def extract(self) -> Dict[str, Any]:
        return {
            "remote_urls": self.extract_urls(),
            "loadstring_invocations": self.extract_loadstrings(),
            "embedded_blobs": self.extract_embedded_blobs(),
            "sensitive_apis": self.extract_sensitive_apis()
        }

    def extract_urls(self) -> List[Dict[str, str]]:
        urls = []
        seen = set()

        # 1. HttpGet / HttpGetAsync
        http_pattern = re.compile(
            r'(?:game|self|Workspace)[\s:]+(?:HttpGet|HttpGetAsync)\s*\(\s*(["\'])(https?://[^\'"]+)\1',
            re.IGNORECASE
        )
        for m in http_pattern.finditer(self.code):
            url = m.group(2)
            if url not in seen:
                seen.add(url)
                urls.append({"url": url, "source": "HttpGet/HttpGetAsync", "safe_preview": url})

        # 2. General HTTP / Webhook endpoints
        general_url_pattern = re.compile(r'https?://[a-zA-Z0-9\-\._~:/\?#\[\]@!$&\'\(\)\*\+,;=%]{8,}')
        for m in general_url_pattern.finditer(self.code):
            url = m.group(0)
            if url not in seen and not url.endswith((".png", ".jpg", ".webp")):
                seen.add(url)
                urls.append({"url": url, "source": "String Constant / Webhook", "safe_preview": url})

        return urls

    def extract_loadstrings(self) -> List[str]:
        invocations = []
        load_pattern = re.compile(r'\b(loadstring|load)\s*\((.*?)\)', re.DOTALL)
        for m in load_pattern.finditer(self.code):
            raw = m.group(0)
            # truncate long bodies for safe report preview
            preview = raw[:160].replace("\n", " ").strip()
            if len(raw) > 160:
                preview += " ... (truncated)"
            invocations.append(preview)
        return invocations

    def extract_embedded_blobs(self) -> List[Dict[str, Any]]:
        blobs = []
        # Check for long base64-like strings (len >= 64)
        b64_pattern = re.compile(r'["\']([A-Za-z0-9+/]{64,}={0,2})["\']')
        for m in b64_pattern.finditer(self.code):
            blob_str = m.group(1)
            # Verify if valid base64
            try:
                decoded = base64.b64decode(blob_str, validate=True)
                blobs.append({
                    "type": "Base64",
                    "length": len(blob_str),
                    "decoded_bytes": len(decoded),
                    "preview": blob_str[:32] + "..."
                })
            except Exception:
                pass
        return blobs

    def extract_sensitive_apis(self) -> List[str]:
        sensitive = [
            "getfenv", "setfenv", "getrenv", "getreg", "getrawmetatable", "setrawmetatable",
            "setreadonly", "make_writeable", "hookfunction", "hookmetamethod",
            "syn.request", "http_request", "request", "readfile", "writefile"
        ]
        found = []
        for api in sensitive:
            matches = len(re.findall(r'\b' + re.escape(api) + r'\b', self.code))
            if matches > 0:
                found.append(f"{api} ({matches} occurrence{'s' if matches > 1 else ''})")
        return found
