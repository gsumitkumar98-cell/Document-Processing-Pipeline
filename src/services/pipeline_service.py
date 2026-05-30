from typing import List

from src.models.search_response import (
    SearchResponse
)

from src.models.retrieval_result import (
    RetrievalResult
)

from src.interfaces.document_loader_interface import (
    DocumentLoaderInterface
)

from src.interfaces.chunker_interface import (
    ChunkerInterface
)

from src.interfaces.repository_interface import (
    RepositoryInterface
)

from src.interfaces.retriever_interface import (
    RetrieverInterface
)

from src.core.logger import get_logger


logger = get_logger(__name__)


class PipelineService:

    def __init__(
        self,
        loader: DocumentLoaderInterface,
        chunker: ChunkerInterface,
        repository: RepositoryInterface,
        retriever: RetrieverInterface
    ):

        self.loader = loader

        self.chunker = chunker

        self.repository = repository

        self.retriever = retriever

    def process_documents(
        self,
        files: List[str]
    ) -> None:

        self.repository.clear()

        for file in files:

            document = (
                self.loader.load(
                    file
                )
            )

            chunks = (
                self.chunker.chunk(
                    document
                )
            )

            self.repository.add_chunks(
                chunks
            )

        logger.info(
            "Document processing completed"
        )

    def search(
        self,
        query: str
    ) -> SearchResponse:

        chunks = (
            self.repository.get_chunks()
        )

        results: List[
            RetrievalResult
        ] = self.retriever.retrieve(
            query,
            chunks
        )

        return SearchResponse(
            query=query,
            total_results=len(results),
            chunks=[
                result.chunk
                for result in results
            ]
        )