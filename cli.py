#!/usr/bin/env python3
"""
CLI entrypoint for Lua Static Source Analyzer & Devirtualization Toolkit.
100% Zero-Execution: Operates on untrusted inputs safely.
"""

import sys
import os
import argparse
import json

from lua_analyzer import LuaStaticAnalyzer

def main():
    parser = argparse.ArgumentParser(
        description="Lua Static Source Analyzer & Devirtualization Toolkit (100% Zero-Execution)"
    )
    parser.add_argument("input", help="Path to input .lua file")
    parser.add_argument("-o", "--output", help="Output directory for cleaned script & reports", default=None)
    parser.add_argument("--json", help="Output analysis metadata as JSON to stdout", action="store_true")

    # Deep Devirtualization & Inspection Options
    parser.add_argument("--deep", help="Enable deep multi-pass static analysis and devirtualization", action="store_true", default=True)
    parser.add_argument("--vm-analysis", help="Perform deep VM boundary and layout recovery", action="store_true", default=True)
    parser.add_argument("--dump-prototypes", help="Dump prototype hierarchy graph", action="store_true", default=False)
    parser.add_argument("--dump-constants", help="Dump constant pools and expressions", action="store_true", default=False)
    parser.add_argument("--dump-opcodes", help="Dump opcode mappings and inferred semantics", action="store_true", default=False)
    parser.add_argument("--dump-cfg", help="Dump Control Flow Graph basic blocks", action="store_true", default=False)
    parser.add_argument("--dump-ir", help="Dump lifted Intermediate Representation (IR)", action="store_true", default=False)
    parser.add_argument("--dump-symbolic", help="Dump symbolic SCCP propagation states", action="store_true", default=False)
    parser.add_argument("--keep-protection", help="Preserve anti-tamper regions in reconstructed code", action="store_true", default=False)
    parser.add_argument("--strict-static", help="Strict zero-execution mode (always enforced)", action="store_true", default=True)
    parser.add_argument("--debug", help="Enable verbose debug logs", action="store_true", default=False)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found '{args.input}'", file=sys.stderr)
        sys.exit(1)

    try:
        options = vars(args)
        analyzer = LuaStaticAnalyzer(args.input, args.output, options=options)
        cleaned_path, report_path, ir_path = analyzer.run_pipeline()

        if args.json:
            print(json.dumps(analyzer.results, indent=2))
        else:
            print("[✓] Lua Static Analysis & Devirtualization Completed Successfully!")
            print(f"  • Cleaned Lua Script:   {cleaned_path}")
            print(f"  • Audit Markdown:       {report_path}")
            print(f"  • Lifted IR Code:       {ir_path}")
            print(f"  • CFG Model Export:     {os.path.join(analyzer.output_dir, os.path.splitext(os.path.basename(args.input))[0] + '_cfg.json')}")
            print(f"  • Prototypes Export:    {os.path.join(analyzer.output_dir, os.path.splitext(os.path.basename(args.input))[0] + '_prototypes.json')}")

    except Exception as e:
        print(f"[!] Analysis Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
