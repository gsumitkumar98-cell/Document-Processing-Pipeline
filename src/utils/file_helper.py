from pathlib import Path

from typing import List


def get_document_files(
    directory: str
) -> List[str]:

    path = Path(directory)

    return [
        str(file)
        for file in path.glob("*.txt")
    ]