from dataclasses import dataclass

from typing import List

from src.models.chunk import Chunk


@dataclass(slots=True)
class SearchResponse:
    """
    Search result model.
    """

    query: str

    total_results: int

    chunks: List[Chunk]