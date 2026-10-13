"""Resolve a pointer chain to a final absolute address.

Chain semantics match Cheat Engine: the *base* address is the first
module-relative address, then each offset is added and dereferenced
in turn. Final offset is added but NOT dereferenced (matches CE's
"pointer" convention for the last hop).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cetm.models.pointer_chain import PointerChain
from cetm.utils.logging_bridge import get_logger

if TYPE_CHECKING:
    from cetm.services.ce_session import CeSession

log = get_logger(__name__)


def resolve_chain(session: "CeSession", chain: PointerChain) -> int | None:
    """Walk a chain in a live process and return the final address.

    Returns None if any hop is unreadable (module missing, page
    unmapped). Never raises for a bad read — pointer scans routinely
    hit stale chains and the caller expects a clean None.
    """
    if not chain.offsets:
        return chain.base

    module_base = session.module_base(chain.module)
    if module_base is None:
        log.debug("module %s not loaded", chain.module)
        return None

    addr = module_base + chain.base
    for off in chain.offsets[:-1]:
        ptr = session.read_u64(addr)
        if ptr is None:
            return None
        addr = ptr + off
    return addr + chain.offsets[-1]