from dataclasses import dataclass


@dataclass(slots=True)
class Chunk:
    """
    Represents a document chunk.
    """

    document_id: str

    document_name: str

    chunk_id: int

    text: str