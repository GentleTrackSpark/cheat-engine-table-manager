"""Output driver: push a CtTable into a live Cheat Engine session."""

from __future__ import annotations

from dataclasses import dataclass

from cetm.models.ct_table import CtTable
from cetm.processors.pointer_resolver import resolve_chain
from cetm.services.ce_session import CeSession
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class EmitResult:
    pushed: int = 0
    failed: int = 0


class CeAttachDriver:
    """Write each entry's resolved address into the live process.

    For static entries (no offsets) we write the address directly.
    For pointer entries we resolve the chain first, then write. A
    failed resolve is counted, not raised — a table with 200 entries
    shouldn't die on entry 7.
    """

    def __init__(self, session: CeSession) -> None:
        self.session = session

    def emit(self, table: CtTable) -> EmitResult:
        result = EmitResult()
        for entry in table.entries:
            target = entry.address
            if entry.offsets:
                target = resolve_chain(self.session, entry.to_pointer_chain())
            if target is None:
                result.failed += 1
                log.debug("entry %d unresolved", entry.id)
                continue
            ok = self.session.write(entry, target)
            if ok:
                result.pushed += 1
            else:
                result.failed += 1
        return result