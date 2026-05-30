from dataclasses import dataclass


@dataclass(slots=True)
class Document:
    """
    Represents a source document.
    """

    document_id: str

    file_name: str

    content: str