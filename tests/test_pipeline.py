from pathlib import Path

from src.services.document_loader import (
    DocumentLoader
)

from src.services.text_chunker import (
    TextChunker
)

from src.services.keyword_retriever import (
    KeywordRetriever
)

from src.repositories.chunk_repository import (
    ChunkRepository
)

from src.services.pipeline_service import (
    PipelineService
)


def test_pipeline():

    file_path = "test_doc.txt"

    Path(
        file_path
    ).write_text(
        "python backend development"
    )

    loader = (
        DocumentLoader()
    )

    chunker = (
        TextChunker(10)
    )

    repository = (
        ChunkRepository()
    )

    retriever = (
        KeywordRetriever()
    )

    pipeline = (
        PipelineService(
            loader,
            chunker,
            repository,
            retriever
        )
    )

    pipeline.process_documents(
        [file_path]
    )

    response = (
        pipeline.search(
            "python"
        )
    )

    assert (
        response.total_results
        == 1
    )

    Path(
        file_path
    ).unlink()