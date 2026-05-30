from src.core.config import settings

from src.repositories.chunk_repository import (
    ChunkRepository
)

from src.services.document_loader import (
    DocumentLoader
)

from src.services.text_chunker import (
    TextChunker
)

from src.services.keyword_retriever import (
    KeywordRetriever
)

from src.services.pipeline_service import (
    PipelineService
)


def get_pipeline_service() -> PipelineService:

    loader = DocumentLoader()

    chunker = TextChunker(
        chunk_size=settings.CHUNK_SIZE
    )

    repository = ChunkRepository()

    retriever = KeywordRetriever()

    return PipelineService(
        loader=loader,
        chunker=chunker,
        repository=repository,
        retriever=retriever
    )