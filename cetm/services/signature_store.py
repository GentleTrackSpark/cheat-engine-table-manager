"""On-disk store for AoB signatures under sigdb/."""

from __future__ import annotations

import json
from pathlib import Path

from cetm.models.signature import AobSignature
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


class SignatureStore:
    """Flat JSON store. One file per module keeps diffs small."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _file_for(self, module: str) -> Path:
        safe = module.replace("/", "_").replace("\\", "_").lower()
        return self.root / f"{safe}.json"

    def load(self, module: str) -> list[AobSignature]:
        f = self._file_for(module)
        if not f.exists():
            return []
        raw = json.loads(f.read_text(encoding="utf-8"))
        return [AobSignature(**rec) for rec in raw]

    def save(self, sigs: list[AobSignature]) -> Path:
        if not sigs:
            raise ValueError("refusing to save empty signature set")
        f = self._file_for(sigs[0].module)
        f.write_text(json.dumps([s.__dict__ for s in sigs], indent=2), encoding="utf-8")
        log.info("saved %d sigs to %s", len(sigs), f.name)
        return f