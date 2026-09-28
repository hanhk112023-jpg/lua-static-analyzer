"""
Static Analyzer Core Pipeline.
Coordinates Lexing, Parsing, Signature Detection, Payload Extraction,
Deobfuscation, Reconstruction, and Reporting.
"""

import os
import hashlib
from typing import Dict, Any, Tuple

from .lexer import LuaLexer
from .parser import LuaParser
from .vm_detector import VMDetector
from .payload_extractor import PayloadExtractor
from .opcode_analyzer import OpcodeAnalyzer
from .ir import IRGenerator
from .deobfuscator import LuaDeobfuscator
from .reconstructor import PseudoLuaReconstructor
from .reporter import AuditReporter

class LuaStaticAnalyzer:
    def __init__(self, input_path: str, output_dir: str = None):
        self.input_path = os.path.abspath(input_path)
        self.output_dir = output_dir or os.path.dirname(self.input_path)
        os.makedirs(self.output_dir, exist_ok=True)

        self.raw_code = ""
        self.sha256 = ""
        self.filesize = 0
        self.results: Dict[str, Any] = {}

    def load_input(self):
        if not os.path.isfile(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        with open(self.input_path, "r", encoding="utf-8", errors="replace") as f:
            self.raw_code = f.read()
        self.filesize = len(self.raw_code)
        self.sha256 = hashlib.sha256(self.raw_code.encode("utf-8")).hexdigest()

    def run_pipeline(self) -> Tuple[str, str, str]:
        self.load_input()

        # 1. Lexer & Parser
        lexer = LuaLexer(self.raw_code)
        tokens = lexer.tokenize()
        parser = LuaParser(tokens)
        ast = parser.parse()

        # 2. VM Signature & Heuristic Detection
        vm_detector = VMDetector(self.raw_code)
        self.results["vm_detector"] = vm_detector.detect()

        # 3. Payload & Remote Loader Extraction (Static, no execution)
        payload_extractor = PayloadExtractor(self.raw_code)
        self.results["payload_extractor"] = payload_extractor.extract()

        # 4. Opcode & Dispatcher Analysis
        opcode_analyzer = OpcodeAnalyzer(self.raw_code)
        self.results["opcode_analyzer"] = opcode_analyzer.analyze()

        # 5. Intermediate Representation (IR) Generation
        ir_gen = IRGenerator()
        for stmt in ast.body:
            ir_gen.lift_ast(stmt)
        ir_text = "\n".join(str(instr) for instr in ir_gen.instructions)

        # 6. Deobfuscation (Unescaping, concat folding, table inlining, arithmetic)
        deobfuscator = LuaDeobfuscator(self.raw_code)
        cleaned_raw, deobf_stats = deobfuscator.deobfuscate()
        self.results["deobfuscation_stats"] = deobf_stats

        # 7. Code Reconstruction & Beautification
        reconstructor = PseudoLuaReconstructor(cleaned_raw)
        final_lua = reconstructor.reconstruct()

        # 8. Report Generation
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        cleaned_path = os.path.join(self.output_dir, f"{base_name}_cleaned.lua")
        report_path = os.path.join(self.output_dir, f"{base_name}_analysis_report.md")
        ir_path = os.path.join(self.output_dir, f"{base_name}_ir.txt")

        with open(cleaned_path, "w", encoding="utf-8") as f:
            f.write(final_lua)

        with open(ir_path, "w", encoding="utf-8") as f:
            f.write(ir_text)

        reporter = AuditReporter(
            filename=os.path.basename(self.input_path),
            filesize=self.filesize,
            sha256=self.sha256,
            analysis_results=self.results
        )
        report_md = reporter.generate_markdown()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        return cleaned_path, report_path, ir_path
