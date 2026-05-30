from src.models.chunk import (
    Chunk
)

from src.repositories.chunk_repository import (
    ChunkRepository
)


def test_add_chunks():

    repository = (
        ChunkRepository()
    )

    repository.add_chunks(
        [
            Chunk(
                document_id="1",
                document_name="doc.txt",
                chunk_id=1,
                text="hello"
            )
        ]
    )

    assert (
        repository.count()
        == 1
    )


def test_clear_repository():

    repository = (
        ChunkRepository()
    )

    repository.add_chunks(
        [
            Chunk(
                document_id="1",
                document_name="doc.txt",
                chunk_id=1,
                text="hello"
            )
        ]
    )

    repository.clear()

    assert (
        repository.count()
        == 0
    )