from abc import ABC
from abc import abstractmethod

from typing import List

from src.models.chunk import Chunk
from src.models.retrieval_result import RetrievalResult


class RetrieverInterface(
    ABC
):

    @abstractmethod
    def retrieve(
        self,
        query: str,
        chunks: List[Chunk]
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks.
        """
        pass