#!/usr/bin/env python3
"""
CLI entrypoint for Lua Static Source Analyzer & Deobfuscator.
"""

import sys
import os
import argparse
import json

from lua_analyzer import LuaStaticAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description="Lua Static Source Analyzer & Security Audit Toolkit (100% Zero-Execution)"
    )
    parser.add_argument("input", help="Path to input .lua file")
    parser.add_argument("-o", "--output", help="Output directory for cleaned script & reports", default=None)
    parser.add_argument("--json", help="Output analysis metadata as JSON to stdout", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found '{args.input}'", file=sys.stderr)
        sys.exit(1)

    try:
        analyzer = LuaStaticAnalyzer(args.input, args.output)
        cleaned_path, report_path, ir_path = analyzer.run_pipeline()

        if args.json:
            print(json.dumps(analyzer.results, indent=2))
        else:
            print("[✓] Lua Static Analysis Completed Successfully!")
            print(f"  • Cleaned Lua Script: {cleaned_path}")
            print(f"  • Audit Markdown:     {report_path}")
            print(f"  • Lifted IR Code:     {ir_path}")

    except Exception as e:
        print(f"[!] Analysis Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
