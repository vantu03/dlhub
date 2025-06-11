from pathlib import Path
from django.conf import settings

class FlagManager:
    FLAGS_DIR = Path(settings.BASE_DIR) / "flags"
    FLAGS_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_flag_path(cls, name):
        return cls.FLAGS_DIR / f"{name}.lock"

    @classmethod
    def enable(cls, name):
        cls.get_flag_path(name).touch()

    @classmethod
    def disable(cls, name):
        cls.get_flag_path(name).unlink(missing_ok=True)

    @classmethod
    def is_enabled(cls, name):
        return cls.get_flag_path(name).exists()

    @classmethod
    def clear(cls):
        if cls.FLAGS_DIR.exists():
            for file in cls.FLAGS_DIR.iterdir():
                if file.is_file():
                    file.unlink()