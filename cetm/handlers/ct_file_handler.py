"""Ingest handler for a single .ct file."""

from __future__ import annotations

from pathlib import Path

from cetm.models.ct_table import CtTable
from cetm.processors.ct_parser import parse_ct
from cetm.processors.ct_validator import validate_table
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


class CtFileHandler:
    """Reads one .ct from disk and returns a validated CtTable."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def ingest(self):
        yield self.ingest_one()

    def ingest_one(self) -> CtTable:
        log.debug("ingest: %s", self.path)
        raw = self.path.read_bytes()
        table = parse_ct(raw, source_path=self.path)
        validate_table(table)
        return table