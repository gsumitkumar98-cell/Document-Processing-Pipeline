from src.models.chunk import (
    Chunk
)

from src.services.keyword_retriever import (
    KeywordRetriever
)


def test_retrieve_chunks():

    chunks = [

        Chunk(
            document_id="1",
            document_name="python.txt",
            chunk_id=1,
            text="python backend api"
        ),

        Chunk(
            document_id="2",
            document_name="ai.txt",
            chunk_id=1,
            text="artificial intelligence"
        )
    ]

    retriever = (
        KeywordRetriever()
    )

    results = (
        retriever.retrieve(
            "python backend",
            chunks
        )
    )

    assert (
        len(results)
        == 1
    )

    assert (
        results[0]
        .chunk
        .document_name
        ==
        "python.txt"
    )