"""AppContext — carried through every command via click's ctx.obj."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cetm.config.settings import Settings, load_settings
from cetm.utils.logging_bridge import configure_logging, get_logger

log = get_logger(__name__)


@dataclass(slots=True)
class AppContext:
    verbose: bool = False
    dry_run: bool = False
    settings: Settings = field(default_factory=load_settings)
    workspace: Path = field(default_factory=lambda: Path.cwd() / "ct_cache")

    def __post_init__(self) -> None:
        configure_logging(debug=self.verbose)
        self.workspace.mkdir(parents=True, exist_ok=True)
        log.debug("app context ready: workspace=%s", self.workspace)