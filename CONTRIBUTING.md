# Contributing to cheat-engine-table-manager

Thanks for wanting to help keep the CT manager alive. This repo is a
pipeline: ingestion handlers pull `.ct` files off disk, processors
normalize and validate them, and output drivers push the result into a
running Cheat Engine instance (or back to disk).

## Ground rules

- **Python 3.11+**. Target Windows 10/11 x64 first; Linux/macOS should
  still import cleanly and run in `--dry-run` mode.
- **No network calls in the core.** Ever. The loader talks to a local CE
  process via `pymem`/`ctypes` and reads local files. If you need to
  download something, it goes behind an explicit `services/` shim and
  is opt-in.
- **Every handler has a schema.** If you add a new CT dialect (CE 6.x,
  CE 7.x, `.CT` from the community), add a matching parser under
  `processors/` and a fixture under `tests/fixtures/`.
- **Tests before PR.** `pytest -q` must be green. New handlers need at
  least one round-trip test.

## Layout

```
bootstrap/     entry points, arg parsing, app wiring
handlers/      ingest side — one handler per source type
processors/    transform side — validate, normalize, sign
drivers/       output side — CE attach, file emit, memory push
services/      long-lived helpers (CE session, sig store, logging)
models/        dataclasses for tables, entries, addresses, jobs
utils/         pure helpers (hex, aob, pointer math, fs)
config/        settings + schema defaults
tests/         pytest suite + fixtures
sigdb/         AoB signature database (community-contributed)
tables/        sample .ct tables + user workspace
```

## Style

- `ruff` + `black`, line length 100.
- Type hints everywhere new code lands.
- Logging via `utils/logging_bridge.py` — never `print()` in core.

## Security notes

- Never commit a `.ct` that targets a live game you don't own. The
  `.gitignore` already covers `tables/*.ct`; keep it that way.
- Signature DB contributions (`sigdb/`) must include the target module
  name and a hash of the first 16 bytes of the module at scan time.

## Reporting

Bugs and feature requests go in Issues. Reverse-engineering writeups
and new CT dialect support are very welcome as PRs.