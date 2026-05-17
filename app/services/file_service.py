import os
from pathlib import Path


def open_path(path: str | Path) -> None:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {path}")

    if os.name == "nt":
        os.startfile(path)
        return

    raise NotImplementedError("Abertura automática implementada apenas para Windows.")