from src.models.document import (
    Document
)

from src.services.text_chunker import (
    TextChunker
)


def test_chunk_document():

    document = Document(
        document_id="1",
        file_name="sample.txt",
        content="a b c d e f"
    )

    chunker = TextChunker(
        chunk_size=2
    )

    chunks = chunker.chunk(
        document
    )

    assert len(
        chunks
    ) == 3

    assert (
        chunks[0].text
        ==
        "a b"
    )