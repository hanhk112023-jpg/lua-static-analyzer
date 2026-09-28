"""
Prototype Extraction & Classification Module.
Recovers VM prototypes, builds the call/nesting graph, and classifies functional roles.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from .constants import ConstantPool

class PrototypeRole:
    BOOTSTRAP = "BOOTSTRAP"
    ANTI_TAMPER = "ANTI_TAMPER"
    VM_RUNTIME = "VM_RUNTIME"
    DECODER = "DECODER"
    APPLICATION_PAYLOAD = "APPLICATION_PAYLOAD"
    UNKNOWN = "UNKNOWN"

class Prototype:
    def __init__(self, prototype_id: int, parent_id: Optional[int] = None):
        self.prototype_id = prototype_id
        self.parent_id = parent_id
        self.instructions: List[Any] = []
        self.constants = ConstantPool(pool_id=f"proto_{prototype_id}")
        self.child_prototypes: List[int] = []
        self.parameters: List[str] = []
        self.upvalues: List[str] = []
        self.register_count: int = 0
        self.source_range: Tuple[int, int] = (0, 0)
        self.role: str = PrototypeRole.UNKNOWN
        self.confidence: float = 0.5
        self.evidence: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prototype_id": self.prototype_id,
            "parent_id": self.parent_id,
            "instruction_count": len(self.instructions),
            "constant_count": len(self.constants.constants),
            "child_prototypes": self.child_prototypes,
            "parameters": self.parameters,
            "upvalues": self.upvalues,
            "register_count": self.register_count,
            "role": self.role,
            "confidence": self.confidence,
            "evidence": self.evidence
        }

class PrototypeGraph:
    def __init__(self):
        self.prototypes: Dict[int, Prototype] = {}
        self.root_id: int = 0

    def add_prototype(self, proto: Prototype):
        self.prototypes[proto.prototype_id] = proto
        if proto.parent_id is not None and proto.parent_id in self.prototypes:
            self.prototypes[proto.parent_id].child_prototypes.append(proto.prototype_id)

    def classify_roles(self):
        """Classifies each prototype based on characteristics, call reachability and structure."""
        for p_id, proto in self.prototypes.items():
            if proto.parent_id is None:
                proto.role = PrototypeRole.BOOTSTRAP
                proto.confidence = 0.85
                proto.evidence.append("Top-level entry prototype (bootstrap)")
            elif any("bit32" in str(i) or "buffer." in str(i) for i in proto.instructions):
                proto.role = PrototypeRole.DECODER
                proto.confidence = 0.80
                proto.evidence.append("Contains bitwise / buffer operations typical of decoders")
            elif len(proto.instructions) > 50:
                proto.role = PrototypeRole.APPLICATION_PAYLOAD
                proto.confidence = 0.75
                proto.evidence.append("Substantial instruction count and application logic")
            else:
                proto.role = PrototypeRole.VM_RUNTIME
                proto.confidence = 0.60
                proto.evidence.append("Helper or sub-routine within VM runtime")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_prototypes": len(self.prototypes),
            "root_id": self.root_id,
            "prototypes": [p.to_dict() for p in self.prototypes.values()]
        }
