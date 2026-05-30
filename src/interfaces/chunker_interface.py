from abc import ABC
from abc import abstractmethod

from typing import List

from src.models.document import Document
from src.models.chunk import Chunk


class ChunkerInterface(
    ABC
):

    @abstractmethod
    def chunk(
        self,
        document: Document
    ) -> List[Chunk]:
        """
        Split document into chunks.
        """
        pass