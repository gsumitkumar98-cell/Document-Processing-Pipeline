from typing import List
from collections.abc import Iterable

from src.models.chunk import Chunk
from src.interfaces.repository_interface import RepositoryInterface


class ChunkRepository(RepositoryInterface):
    """
    In-memory chunk repository with data validation and encapsulation.
    """

    def __init__(self) -> None:
        self._chunks: List[Chunk] = []

    def add_chunks(self, chunks: Iterable[Chunk]) -> None:
        """
        Add chunks to repository with validation.
        
        Args:
            chunks: Iterable of Chunk instances
            
        Raises:
            TypeError: If chunks is not iterable or contains non-Chunk instances
            ValueError: If chunks is empty or None
        """
        if chunks is None:
            raise ValueError("Chunks cannot be None")
        
        if not isinstance(chunks, Iterable):
            raise TypeError("Chunks must be an iterable collection")
        
        chunk_list = list(chunks)
        
        if not chunk_list:
            raise ValueError("Cannot add empty chunk collection")
        
        for idx, chunk in enumerate(chunk_list):
            if not isinstance(chunk, Chunk):
                raise TypeError(
                    f"Item at index {idx} is not a Chunk instance: {type(chunk).__name__}"
                )
        
        self._chunks.extend(chunk_list)

    def get_chunks(self) -> List[Chunk]:
        """
        Retrieve all chunks as a defensive copy.
        
        Returns:
            A copy of the chunks list to prevent external mutation
        """
        return self._chunks.copy()

    def clear(self) -> None:
        """
        Clear all chunks from repository.
        """
        self._chunks.clear()

    def count(self) -> int:
        """
        Return total chunk count.
        
        Returns:
            Number of chunks in repository
        """
        return len(self._chunks)