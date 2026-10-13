"""Ingest handler for cached pointer-scan results (JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from cetm.models.pointer_chain import PointerChain
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


class PointerScanHandler:
    """Reads a .ptr.json cache produced by a previous scan run.

    Each record is validated against PointerChain.from_record(); bad
    records are dropped, not raised, so a partially-written cache
    (crash mid-scan) is still usable.
    """

    def __init__(self, cache_file: Path) -> None:
        self.cache_file = Path(cache_file)

    def ingest(self) -> Iterator[PointerChain]:
        if not self.cache_file.exists():
            log.warning("no pointer cache at %s", self.cache_file)
            return
        data = json.loads(self.cache_file.read_text(encoding="utf-8"))
        records = data.get("chains", []) if isinstance(data, dict) else data
        for rec in records:
            try:
                yield PointerChain.from_record(rec)
            except (KeyError, TypeError, ValueError) as exc:
                log.debug("drop bad chain: %s", exc)