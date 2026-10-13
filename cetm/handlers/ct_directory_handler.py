"""Ingest handler that walks a directory tree for .ct files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from cetm.handlers.ct_file_handler import CtFileHandler
from cetm.models.ct_table import CtTable
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)

_SKIP_DIRS = {"__pycache__", ".git", ".venv", "node_modules", "ct_cache"}


class CtDirectoryHandler:
    """Recursively yields every parseable CtTable under ``root``.

    Unparseable files are logged and skipped — a broken table in a
    folder shouldn't abort the whole scan.
    """

    def __init__(self, root: Path, *, follow_symlinks: bool = False) -> None:
        self.root = Path(root)
        self.follow_symlinks = follow_symlinks

    def ingest(self) -> Iterator[CtTable]:
        for path in self._iter_cts():
            try:
                yield CtFileHandler(path).ingest_one()
            except Exception as exc:  # noqa: BLE001 - scan must not abort
                log.warning("skip %s: %s", path, exc)

    def _iter_cts(self) -> Iterator[Path]:
        for p in self.root.rglob("*.ct"):
            if any(part in _SKIP_DIRS for part in p.parts):
                continue
            if p.is_symlink() and not self.follow_symlinks:
                continue
            yield p