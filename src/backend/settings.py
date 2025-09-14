"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

from platformdirs import user_config_dir


@dataclass
class SettingsData:
    """Stores user preferences and recent files."""
    first_time_running: bool = True
    recently_saved: list[str] = field(default_factory=list)

    def update_recently_saved(self, path: str) -> None:
        """Updates the recently saved list with the given path."""
        if path in self.recently_saved:
            self.recently_saved.remove(path)
        self.recently_saved.insert(0, path)
        self.recently_saved = self.recently_saved[:5]


class Settings:
    """Persistent settings manager."""

    def __init__(self):
        self.config_path = Path(user_config_dir("GAVL")) / "config.json"
        self.data: SettingsData = self._load()

    def _load(self) -> SettingsData:
        """Load settings from the config file or return defaults if missing/corrupted."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    raw = json.load(f)
                return SettingsData(**raw)  # map JSON into dataclass
            except (json.JSONDecodeError, TypeError):
                # Fallback to defaults if corrupted
                return SettingsData()
        else:
            return SettingsData()

    def save(self) -> None:
        """Save current settings to the config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(asdict(self.data), f, indent=4)

    def __repr__(self) -> str:
        return f"<Settings {self.data}>"
