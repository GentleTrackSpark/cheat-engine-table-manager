"""PointerChain — a module-relative base plus dereference offsets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PointerChain:
    module: str
    base: int
    offsets: list[int] = field(default_factory=list)

    @classmethod
    def from_record(cls, rec: dict[str, Any]) -> "PointerChain":
        """Build from a pointer-s