"""Structural + semantic validation for a parsed CtTable."""

from __future__ import annotations

from cetm.models.ct_table import CtTable
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)

_MAX_ENTRIES = 20_000
_MAX_OFFSET_DEPTH = 8


class CtValidationError(ValueError):
    """Raised when a table is structurally unusable."""


def validate_table(table: CtTable) -> None:
    """Raise CtValidationError if the table can't be loaded safely.

    Checks:
      - entry count within sane bounds
      - every entry has a description (empty ones are dropped, not fatal)
      - pointer chains don't exceed _MAX_OFFSET_DEPTH
      - addresses, when present, fit in 64 bits
    """
    if len(table.entries) > _MAX_ENTRIES:
        raise CtValidationError(f"entry count {len(table.entries)} exceeds {_MAX_ENTRIES}")

    dropped = 0
    kept = []
    for e in table.entries:
        if not e.description:
            dropped += 1
            continue
        if len(e.offsets) > _MAX_OFFSET_DEPTH:
            raise CtValidationError(f"entry {e.id} offset depth {len(e.offsets)} too deep")
        if e.address is not None and (e.address < 0 or e.address > 0xFFFF_FFFF_FFFF_FFFF):
            raise CtValidationError(f"entry {e.id} address out of 64-bit range")
        kept.append(e)

    if dropped:
        log.info("dropped %d entries with empty description", dropped)
    table.entries = kept