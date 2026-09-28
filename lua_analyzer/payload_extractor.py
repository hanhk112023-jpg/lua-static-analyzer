"""
Semantic Payload Extractor Module.
Statically locates and resolves remote payloads, URLs, and dynamic execution endpoints.
Tracks resolution method, provenance, and confidence without executing any untrusted code.
"""

import re
import base64
from typing import Dict, List, Any

class ResolutionMethod:
    STATIC_LITERAL = "STATIC_LITERAL"
    CONCAT_FOLD = "CONCAT_FOLD"
    CONST_DECODER = "CONST_DECODER"
    XOR_DECODER = "XOR_DECODER"
    TABLE_RECONSTRUCTION = "TABLE_RECONSTRUCTION"
    PARTIAL_SYMBOLIC = "PARTIAL_SYMBOLIC"
    UNRESOLVED = "UNRESOLVED"

class ExtractedURL:
    def __init__(self, original_expression: str, resolved_value: str, method: str, confidence: float, source_api: str):
        self.original_expression = original_expression
        self.resolved_value = resolved_value
        self.resolution_method = method
        self.confidence = confidence
        self.source_api = source_api

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.resolved_value,
            "source": self.source_api,
            "original_expression": self.original_expression,
            "resolved_value": self.resolved_value,
            "resolution_method": self.resolution_method,
            "confidence": self.confidence,
            "source_api": self.source_api
        }

class PayloadExtractor:
    def __init__(self, code: str):
        self.code = code

    def extract(self) -> Dict[str, Any]:
        return {
            "remote_urls": [u.to_dict() for u in self.extract_urls()],
            "loadstring_invocations": self.extract_loadstrings(),
            "embedded_blobs": self.extract_embedded_blobs(),
            "sensitive_apis": self.extract_sensitive_apis()
        }

    def extract_urls(self) -> List[ExtractedURL]:
        urls: List[ExtractedURL] = []
        seen = set()

        # 1. HttpGet / HttpGetAsync with literal or concatenated strings
        http_pattern = re.compile(
            r'(?:game|self|Workspace)[\s:]+(?:HttpGet|HttpGetAsync)\s*\(\s*(.*?)\s*\)',
            re.IGNORECASE
        )
        for m in http_pattern.finditer(self.code):
            raw_arg = m.group(1).strip()
            # If literal string
            if raw_arg.startswith(('"', "'")):
                url_val = raw_arg[1:-1]
                if url_val.startswith("http") and url_val not in seen:
                    seen.add(url_val)
                    urls.append(ExtractedURL(
                        original_expression=m.group(0),
                        resolved_value=url_val,
                        method=ResolutionMethod.STATIC_LITERAL,
                        confidence=1.0,
                        source_api="HttpGet"
                    ))
            elif ".." in raw_arg:
                # Concatenation expression
                parts = re.findall(r'["\']([^"\']+)["\']', raw_arg)
                combined = "".join(parts)
                if combined.startswith("http") and combined not in seen:
                    seen.add(combined)
                    urls.append(ExtractedURL(
                        original_expression=m.group(0),
                        resolved_value=combined,
                        method=ResolutionMethod.CONCAT_FOLD,
                        confidence=0.95,
                        source_api="HttpGet(Concat)"
                    ))
            else:
                # Variable or dynamic expression
                # Search if there is a variable assignment earlier: local var = "http..."
                var_match = re.search(r'\b' + re.escape(raw_arg) + r'\s*=\s*["\'](https?://[^"\']+)["\']', self.code)
                if var_match:
                    found_url = var_match.group(1)
                    if found_url not in seen:
                        seen.add(found_url)
                        urls.append(ExtractedURL(
                            original_expression=f"{raw_arg} -> {m.group(0)}",
                            resolved_value=found_url,
                            method=ResolutionMethod.PARTIAL_SYMBOLIC,
                            confidence=0.90,
                            source_api="HttpGet(VariableRef)"
                        ))

        # 2. General HTTP / Webhook URLs
        general_pattern = re.compile(r'https?://[a-zA-Z0-9\-\._~:/\?#\[\]@!$&\'\(\)\*\+,;=%]{8,}')
        for m in general_pattern.finditer(self.code):
            url_str = m.group(0)
            if url_str not in seen and not url_str.endswith((".png", ".jpg", ".webp")):
                seen.add(url_str)
                urls.append(ExtractedURL(
                    original_expression=url_str,
                    resolved_value=url_str,
                    method=ResolutionMethod.STATIC_LITERAL,
                    confidence=0.85,
                    source_api="StringLiteral"
                ))

        return urls

    def extract_loadstrings(self) -> List[str]:
        invocations = []
        load_pattern = re.compile(r'\b(loadstring|load)\s*\((.*?)\)', re.DOTALL)
        for m in load_pattern.finditer(self.code):
            raw = m.group(0)
            preview = raw[:160].replace("\n", " ").strip()
            if len(raw) > 160:
                preview += " ... (truncated)"
            invocations.append(preview)
        return invocations

    def extract_embedded_blobs(self) -> List[Dict[str, Any]]:
        blobs = []
        b64_pattern = re.compile(r'["\']([A-Za-z0-9+/]{64,}={0,2})["\']')
        for m in b64_pattern.finditer(self.code):
            blob_str = m.group(1)
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
