import sys
from pathlib import Path


def get_base_dir() -> Path:
    """
    Retorna a pasta base do projeto/app.

    Em desenvolvimento:
    kit-app/

    No app empacotado com PyInstaller:
    pasta onde está o .exe
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent.parent


def get_resource_path(relative_path: str) -> Path:
    return get_base_dir() / relative_path