"""Output driver: write derived data back to disk as JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from cetm.models.ct_table import CtTable
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


class FileEmitDriver:
    """Emit tables, module maps, and scan results to a workspace dir."""

    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def write_table(self, table: CtTable, name: str | None = None) -> Path:
        out = self.out_dir / (name or f"{table.path.stem}.parsed.json")
        payload = {
            "source": str(table.path),
            "ce_version": table.ce_version,
            "entries": [asdict(e) for e in table.entries],
        }
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        log.info("wrote %s", out)
        return out

    def write_modules(self, modules: list[dict]) -> Path:
        pid = modules[0].get("pid", 0) if modules else 0
        out = self.out_dir / f"modules_{pid}.json"
        out.write_text(json.dumps(modules, indent=2), encoding="utf-8")
        return out