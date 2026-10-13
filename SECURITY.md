# Security Policy

## Scope

`cheat-engine-table-manager` is a **local desktop tool**. It reads
`.ct` (Cheat Engine table) files from disk, parses them, and drives a
locally-running Cheat Engine process. It does not phone home, does not
run a server, and does not accept remote input.

## Threat model

The realistic risks are:

1. **Malicious `.ct` files.** A `.ct` is XML with embedded Lua
   (`<CheatTable><CheatEntries><CheatEntry><AssemblerScript>` etc.).
   Cheat Engine itself will execute that Lua on load. This tool does
   **not** execute embedded Lua during parse — it only reads the XML
   tree and extracts addresses, AOBs, and metadata. Execution only
   happens if you explicitly hand the table to a running CE instance
   via a driver, which is the same trust boundary CE already has.
2. **Pointer-scan cache poisoning.** The local pointer cache
   (`ct_cache/`) is JSON. If an attacker can write to your user profile
   they can already do worse. We still validate every cached record on
   load and drop malformed ones.
3. **DLL / process attach.** `services/ce_session.py` attaches to a
   process by name/PID using `pymem`. It does not load DLLs. If a
   future driver needs `LoadLibrary`, it goes through an explicit
   `--allow-inject` flag and a confirmation prompt.

## Reporting a vulnerability

Open a private security advisory on GitHub. Include:

- Repo commit SHA
- The `.ct` or input that triggers it
- CE version + Windows build
- Whether CE was running at the time

We aim to acknowledge within 72 hours.

## Out of scope

- Getting banned in a game. That's on you.
- Anti-cheat detection. This is not an evasion tool; it's a table
  manager. If you need an injector/spoofer, that's a different repo.
- Anything that happens once you hand a table to CE. CE is the
  executor; we're the librarian.