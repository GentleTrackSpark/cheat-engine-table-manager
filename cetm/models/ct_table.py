"""CtTable and CtEntry — the core in-memory representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cetm.models.pointer_chain import PointerChain


@dataclass(slots=True)
class CtEntry:
    """A single row from a Cheat Engine table."""

    id: int
    description: str
    variable_type: str
    size: int
    address: int | None = None
    offsets: list[int] = field(default_factory=list)

    def to_pointer_chain(self, module: str = "game.exe") -> PointerChain:
        """Best-effort conversion to a PointerChain for resolution.

        The module is a guess — CT files don't carry it explicitly.
        Callers that know the target module should override it.
        """
        return PointerChain(
            module=module,
            base=self.address or 0,
            offsets=list(self.offsets),
        )


@dataclass(slots=True)
class CtTable:
    """A parsed .ct file."""

    path: Path
    ce_version: str
    entries: list[CtEntry]

    @property
    def entry_count(self) -> int:
        return len(self.entries)