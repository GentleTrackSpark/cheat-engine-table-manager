"""Handler protocol. Every ingest source implements this."""

from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from cetm.models.ct_table import CtTable


@runtime_checkable
class Handler(Protocol):
    """A source of CtTable objects.

    Implementations may be lazy (generators) or eager (lists). The
    pipeline consumes ``ingest()`` once and expects it to be
    idempotent-ish: calling it twice re-reads the source.
    """

    def ingest(self) -> Iterator[CtTable]:
        ...