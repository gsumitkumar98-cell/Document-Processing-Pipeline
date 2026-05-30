from abc import ABC
from abc import abstractmethod

from typing import List

from src.models.chunk import Chunk


class RepositoryInterface(
    ABC
):

    @abstractmethod
    def add_chunks(
        self,
        chunks: List[Chunk]
    ) -> None:
        pass

    @abstractmethod
    def get_chunks(
        self
    ) -> List[Chunk]:
        pass

    @abstractmethod
    def clear(
        self
    ) -> None:
        pass