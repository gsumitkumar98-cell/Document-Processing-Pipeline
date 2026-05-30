from abc import ABC
from abc import abstractmethod

from src.models.document import Document


class DocumentLoaderInterface(
    ABC
):

    @abstractmethod
    def load(
        self,
        file_path: str
    ) -> Document:
        """
        Load document from source.
        """
        pass