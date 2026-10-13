"""CLI entry point for cetm.

Subcommands map 1:1 onto pipeline stages:
    cetm scan   <dir>          -> ingest handlers walk a directory
    cetm show   <table.ct>     -> parse + pretty-print entries
    cetm load   <table.ct>     -> attach CE, push entries as a job
    cetm dump   <pid>          -> dump module map for sig work
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from cetm.bootstrap.app import AppContext
from cetm.drivers.ce_attach_driver import CeAttachDriver
from cetm.drivers.file_emit_driver import FileEmitDriver
from cetm.handlers.ct_directory_handler import CtDirectoryHandler
from cetm.handlers.ct_file_handler import CtFileHandler
from cetm.services.ce_session import CeSession
from cetm.utils.logging_bridge import get_logger

log = get_logger(__name__)
console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--verbose", is_flag=True, help="Debug-level logging.")
@click.option("--dry-run", is_flag=True, help="Never touch a live CE process.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, dry_run: bool) -> None:
    ctx.obj = AppContext(verbose=verbose, dry_run=dry_run)
    log.debug("bootstrap: verbose=%s dry_run=%s", verbose, dry_run)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.pass_obj
def scan(app: AppContext, directory: Path) -> None:
    """Walk a directory and list every CT table found."""
    handler = CtDirectoryHandler(directory)
    tables = list(handler.ingest())
    console.print(f"[bold]found[/] {len(tables)} table(s) under {directory}")
    for t in tables:
        console.print(f"  [cyan]{t.path.name}[/]  entries={len(t.entries)}  ce={t.ce_version}")


@cli.command()
@click.argument("table", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_obj
def show(app: AppContext, table: Path) -> None:
    """Parse a single .ct and print its entries."""
    handler = CtFileHandler(table)
    parsed = handler.ingest_one()
    console.print(f"[bold]{parsed.path.name}[/]  ce={parsed.ce_version}  entries={len(parsed.entries)}")
    for e in parsed.entries:
        addr = f"0x{e.address:08X}" if e.address is not None else "?"
        console.print(f"  [green]{addr}[/]  {e.description}")


@cli.command()
@click.argument("table", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--process", "process_name", required=True, help="Target process name, e.g. game.exe")
@click.pass_obj
def load(app: AppContext, table: Path, process_name: str) -> None:
    """Attach to a process and push a table's entries as a job."""
    parsed = CtFileHandler(table).ingest_one()
    if app.dry_run:
        console.print("[yellow]dry-run:[/] would attach to", process_name)
        return
    with CeSession(process_name) as session:
        driver = CeAttachDriver(session)
        result = driver.emit(parsed)
    console.print(f"[bold green]pushed[/] {result.pushed} entries, {result.failed} failed")


@cli.command()
@click.argument("pid", type=int)
@click.pass_obj
def dump(app: AppContext, pid: int) -> None:
    """Dump the module map of a PID (for signature work)."""
    with CeSession.by_pid(pid) as session:
        modules = session.module_map()
    out = FileEmitDriver(Path("logs"))
    out.write_modules(modules)
    console.print(f"wrote {len(modules)} modules to logs/modules_{pid}.json")


def main() -> int:
    try:
        cli(standalone_mode=False)
    except click.ClickException as e:
        e.show()
        return e.exit_code
    return 0


if __name__ == "__main__":
    sys.exit(main())