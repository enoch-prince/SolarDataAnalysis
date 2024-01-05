from pathlib import Path
from typing import Generator

DEBUG = False

def resolveDataFolderPaths(path_str: str):
    path = Path(path_str)

    path_exists = path.exists()
    if DEBUG:
        print("\nDoes path exist: ", path_exists, "\n")

    if path_exists:
        folder_name = path.parts[-1]
        return folder_name,path.glob("**")

def resolveCSVFilePaths(folder_path: Path) -> Generator[Path, None, None] | None:
    return folder_path.glob("*.csv")