from dataclasses import dataclass

from src.models.chunk import Chunk


@dataclass(slots=True)
class RetrievalResult:
    score: float
    chunk: Chunk