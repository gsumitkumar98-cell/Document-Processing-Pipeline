from pathlib import Path

from src.core.constants import (
    SUPPORTED_EXTENSIONS
)

from src.core.exceptions import (
    DocumentLoadException
)


def validate_document(
    file_path: str
) -> None:

    path = Path(file_path)

    if not path.exists():

        raise DocumentLoadException(
            f"File not found: {file_path}"
        )

    if path.suffix.lower() not in (
        SUPPORTED_EXTENSIONS
    ):

        raise DocumentLoadException(
            f"Unsupported file type: {path.suffix}"
        )