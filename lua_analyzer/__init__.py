"""
Lua Static Analyzer & Devirtualization Toolkit.
Pipeline:
Input Lua/Luau -> Lexer -> Parser / AST -> Protection Detection
-> VM Boundary Detection -> Prototype Extraction -> VM Memory/Layout Recovery
-> Constant Extraction -> Encoded Constant Analysis -> Opcode/Operand Recovery
-> Opcode Semantic Inference -> Virtual Register Dataflow -> SSA -> SCCP
-> CFG Reconstruction -> Dispatcher Devirtualization -> Dead/Junk Code Elimination
-> String/Constant Decryption -> Expression Reconstruction -> Structured Control Flow
-> Variable Recovery -> Pseudo-Lua Reconstruction -> Security/Audit Report
"""

__version__ = "2.0.0"

from .lexer import LuaLexer, Token, TokenType
from .parser import LuaParser, ASTNode
from .analyzer import LuaStaticAnalyzer
from .vm_detector import VMDetector, VMSignature
from .vm_boundary import VMBoundaryDetector, VMLayout
from .soa import SoAAnalyzer, SoAMapping
from .prototype import Prototype, PrototypeGraph, PrototypeRole
from .constants import ConstExpr, ConstantPool, SymbolicConstantEvaluator
from .bitvector import BitVector
from .decoder import DecoderFunction, DecoderAnalyzer, DecoderResolution
from .payload_extractor import PayloadExtractor, ResolutionMethod, ExtractedURL
from .opcode_recovery import OpcodeRecoverer, OpcodeDefinition, SemanticCategory
from .ir import IRGenerator, IRInstruction, Opcode
from .cfg import ControlFlowGraph, BasicBlock
from .dataflow import DataflowAnalyzer
from .ssa import SCCP, SSAVar, PhiNode
from .dispatcher import DispatcherDevirtualizer, DispatcherModel
from .deobfuscator import LuaDeobfuscator
from .reconstructor import PseudoLuaReconstructor
from .reporter import AuditReporter
