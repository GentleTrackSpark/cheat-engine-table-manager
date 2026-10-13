"""Turn a byte pattern into a stable signature record."""

from __future__ import annotations

import hashlib

from cetm.models.signature import AobSignature
from cetm.utils.aob_tools import normalize_pattern


def sign_pattern(pattern: str, *, module: str, scan_module_size: int) -> AobSignature:
    """Hash a normalized AoB pattern into a stable signature id.

    The id is sha1(normalized_pattern + module + size) truncated to 16
    hex chars. Same pattern against the same module at the same size
    always yields the same id, so signatures dedupe naturally in
    sigdb/.
    """
    norm = normalize_pattern(pattern)
    h = hashlib.sha1()
    h.update(norm.encode("ascii"))
    h.update(b"|")
    h.update(module.encode("utf-8"))
    h.update(b"|")
    h.update(str(scan_module_size).encode("ascii"))
    return AobSignature(
        sig_id=h.hexdigest()[:16],
        pattern=norm,
        module=module,
        module_size=scan_module_size,
    )