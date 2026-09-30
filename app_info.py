import sys
from pathlib import Path

APP_NAME = "Birim Dönüştürücü"
VERSION = "0.1.0"
AUTHOR = "Miraç Deprem"
REPOSITORY_URL = "https://github.com/MrcDprm/unit-converter"


def resource_path(relative_path):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return str(base_path / relative_path)
