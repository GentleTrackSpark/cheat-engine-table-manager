"""Attach to a running process and read/write memory.

Wraps pymem. Context-manager so the handle closes cleanly even on
error. All reads return None on failure rather than raising — the
resolver and driver layers treat None as "chain broken, skip".
"""

from __future__ import annotations

from types import TracebackType
from typing import Any

import pymem
import pymem.process

from cetm.models.ct_table import CtEntry
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)


class CeSession:
    """A live handle to a target process.

    Usage:
        with CeSession("game.exe") as s:
            addr = s.module_base("game.exe")
    """

    def __init__(self, process_name: str) -> None:
        self._process_name = process_name
        self._pm: pymem.Pymem | None = None
        self._modules: dict[str, tuple[int, int]] = {}

    @classmethod
    def by_pid(cls, pid: int) -> "CeSession":
        s = cls.__new__(cls)
        s._process_name = f"pid:{pid}"
        s._pm = None
        s._modules = {}
        s._attach_pid(pid)
        return s

    def _attach_pid(self, pid: int) -> None:
        self._pm = pymem.Pymem()
        self._pm.open_process_from_id(pid)
        self._refresh_modules()

    def __enter__(self) -> "CeSession":
        if self._pm is None:
            log.info("attaching to %s", self._process_name)
            self._pm = pymem.Pymem(self._process_name)
            self._refresh_modules()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._pm is not None:
            try:
                self._pm.close_process()
            except Exception:  # noqa: BLE001
                pass
            self._pm = None

    def _refresh_modules(self) -> None:
        assert self._pm is not None
        self._modules = {}
        for mod in pymem.process.list_modules(self._pm.process_handle):
            self._modules[mod.name.lower()] = (mod.lpBaseOfDll, mod.SizeOfImage)

    def module_base(self, name: str) -> int | None:
        entry = self._modules.get(name.lower())
        return entry[0] if entry else None

    def module_map(self) -> list[dict[str, Any]]:
        pid = self._pm.process_id if self._pm else 0
        return [
            {"pid": pid, "name": n, "base": base, "size": size}
            for n, (base, size) in sorted(self._modules.items())
        ]

    def read_u64(self, address: int) -> int | None:
        if self._pm is None:
            return None
        try:
            return int.from_bytes(self._pm.read_bytes(address, 8), "little")
        except Exception:  # noqa: BLE001
            return None

    def write(self, entry: CtEntry, target: int) -> bool:
        if self._pm is None or entry.size == 0:
            return False
        try:
            self._pm.write_bytes(target, (0).to_bytes(entry.size, "little"), entry.size)
            return True
        except Exception:  # noqa: BLE001
            return False