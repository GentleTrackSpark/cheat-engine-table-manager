"""Parse a Cheat Engine .ct (XML) blob into a CtTable.

The .ct format is XML with the shape:

    <CheatTable CheatEngineTableVersion="46">
      <CheatEntries>
        <CheatEntry>
          <ID>0</ID>
          <Description>"hp"</Description>
          <VariableType>4 Bytes</VariableType>
          <Address>00ABCDEF</Address>
          <Offsets><Offset>10</Offset></Offsets>
        </CheatEntry>
      </CheatEntries>
    </CheatTable>

We deliberately do NOT evaluate the embedded <AssemblerScript> Lua.
Parsing is side-effect free; execution only happens when a driver
hands the table to a live CE instance.
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from cetm.models.ct_table import CtEntry, CtTable
from cetm.utils.hex_tools import parse_ce_hex
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)

_VAR_TYPE_MAP = {
    "Byte": 1,
    "2 Bytes": 2,
    "4 Bytes": 4,
    "8 Bytes": 8,
    "Float": 4,
    "Double": 8,
    "String": 0,
    "Array of byte": 0,
}


def parse_ct(raw: bytes, *, source_path: Path | None = None) -> CtTable:
    """Parse raw .ct bytes into a CtTable.

    Raises lxml.etree.XMLSyntaxError on malformed XML. Raises
    ValueError if the root element is not <CheatTable>.
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    root = etree.fromstring(raw, parser=parser)
    if root.tag != "CheatTable":
        raise ValueError(f"not a CheatTable root: {root.tag!r}")

    ce_version = root.get("CheatEngineTableVersion", "unknown")
    entries: list[CtEntry] = []
    for idx, node in enumerate(root.iter("CheatEntry")):
        entries.append(_parse_entry(node, idx))

    table = CtTable(
        path=source_path or Path("<memory>"),
        ce_version=ce_version,
        entries=entries,
    )
    log.debug("parsed %d entries from %s", len(entries), table.path.name)
    return table


def _parse_entry(node: etree._Element, idx: int) -> CtEntry:
    desc = _text(node, "Description").strip('"')
    vtype = _text(node, "VariableType") or "4 Bytes"
    addr_text = _text(node, "Address")
    address = parse_ce_hex(addr_text) if addr_text else None
    offsets = [parse_ce_hex(o.text or "") for o in node.iter("Offset") if o.text]
    return CtEntry(
        id=idx,
        description=desc,
        variable_type=vtype,
        size=_VAR_TYPE_MAP.get(vtype, 4),
        address=address,
        offsets=[o for o in offsets if o is not None],
    )


def _text(node: etree._Element, tag: str) -> str:
    el = node.find(tag)
    if el is None or el.text is None:
        return ""
    return el.text