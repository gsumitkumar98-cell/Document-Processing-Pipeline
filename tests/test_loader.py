from pathlib import Path

from src.services.document_loader import (
    DocumentLoader
)


def test_load_document():

    file_path = "temp.txt"

    Path(
        file_path
    ).write_text(
        "Python Backend Development"
    )

    loader = DocumentLoader()

    document = loader.load(
        file_path
    )

    assert (
        document.content
        ==
        "Python Backend Development"
    )

    assert (
        document.file_name
        ==
        "temp.txt"
    )

    Path(
        file_path
    ).unlink()