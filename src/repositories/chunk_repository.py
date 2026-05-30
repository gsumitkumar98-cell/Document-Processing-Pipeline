from typing import List

from src.models.chunk import Chunk

from src.interfaces.repository_interface import (
    RepositoryInterface
)


class ChunkRepository(
    RepositoryInterface
):
    """
    In-memory chunk repository.
    """

    def __init__(self) -> None:

        self._chunks: List[
            Chunk
        ] = []

    def add_chunks(
        self,
        chunks: List[Chunk]
    ) -> None:
        """
        Add chunks to repository.
        """

        self._chunks.extend(
            chunks
        )

    def get_chunks(
        self
    ) -> List[Chunk]:
        """
        Retrieve all chunks.
        """

        return self._chunks

    def clear(
        self
    ) -> None:
        """
        Clear repository.
        """

        self._chunks.clear()

    def count(
        self
    ) -> int:
        """
        Return chunk count.
        """

        return len(
            self._chunks
        )