"""
Lua Static Analyzer & Deobfuscation Toolkit
Pipeline: Lua Input -> Lexer/Parser -> Static Analyzer -> VM Detector -> Payload Extractor
          -> Opcode Analyzer -> IR -> Control Flow Analysis -> Deobfuscation
          -> Pseudo-Lua Reconstruction -> Report
"""

__version__ = "1.0.0"

from .lexer import LuaLexer, Token, TokenType
from .parser import LuaParser, ASTNode
from .analyzer import LuaStaticAnalyzer
from .vm_detector import VMDetector, VMSignature
from .payload_extractor import PayloadExtractor
from .opcode_analyzer import OpcodeAnalyzer
from .ir import IRGenerator, IRInstruction
from .cfg import ControlFlowGraph
from .deobfuscator import LuaDeobfuscator
from .reconstructor import PseudoLuaReconstructor
from .reporter import AuditReporter
