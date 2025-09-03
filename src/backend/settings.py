import json
from pathlib import Path
from platformdirs import user_config_dir
from dataclasses import dataclass, asdict, field


@dataclass
class SettingsData:
    """Define your settings here with types and defaults."""
    first_time_running: bool = True
    recently_saved: list[str] = field(default_factory=list)

    def update_recently_saved(self, path: str) -> None:
        """Updates the recently saved list with the given path."""
        if path in self.recently_saved:
            self.recently_saved.remove(path)
        self.recently_saved.insert(0, path)
        self.recently_saved = self.recently_saved[:5]


class Settings:
    """
    Persistent settings manager with IDE hinting via dataclass.
    Example:
        settings = Settings("MyApp", "MyCompany")
        print(settings.data.theme) # autocomplete works
        settings.data.theme = "dark"
        settings.save()
    """

    def __init__(self):
        self.config_path = Path(user_config_dir("GAVL")) / "config.json"
        self.data: SettingsData = self._load()

    def _load(self) -> SettingsData:
        """Load settings from the config file, or return defaults if missing/corrupted."""
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



# ---------------- Example Usage -----------------
if __name__ == "__main__":
    settings = Settings()

    print("Theme:", settings.data.first_time_running)
    settings.data.first_time_running = False
    settings.save()
    print("Updated settings:", settings)