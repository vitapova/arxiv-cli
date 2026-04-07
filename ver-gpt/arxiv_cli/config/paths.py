from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_dir


APP_NAME = "arxiv-cli"


@dataclass(frozen=True)
class DataPaths:
    data_dir: Path

    @property
    def library_path(self) -> Path:
        return self.data_dir / "library.json"

    @property
    def subscriptions_path(self) -> Path:
        return self.data_dir / "subscriptions.json"

    @property
    def state_dir(self) -> Path:
        return self.data_dir / "state"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"


def default_data_dir() -> Path:
    return Path(user_data_dir(APP_NAME))


def get_paths(data_dir: Path | None = None) -> DataPaths:
    base = data_dir or default_data_dir()
    base.mkdir(parents=True, exist_ok=True)
    (base / "state").mkdir(parents=True, exist_ok=True)
    (base / "cache").mkdir(parents=True, exist_ok=True)
    return DataPaths(data_dir=base)
