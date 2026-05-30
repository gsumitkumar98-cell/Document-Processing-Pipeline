from typing import List

from src.models.chunk import Chunk
from src.models.document import Document

from src.interfaces.chunker_interface import (
    ChunkerInterface
)

from src.core.exceptions import (
    ChunkingException
)

from src.core.logger import get_logger


logger = get_logger(__name__)


class TextChunker(
    ChunkerInterface
):

    def __init__(
        self,
        chunk_size: int
    ):

        self.chunk_size = chunk_size

    def chunk(
        self,
        document: Document
    ) -> List[Chunk]:

        try:

            words = (
                document.content.split()
            )

            chunks = []

            chunk_id = 1

            for index in range(
                0,
                len(words),
                self.chunk_size
            ):

                text = " ".join(
                    words[
                        index:
                        index +
                        self.chunk_size
                    ]
                )

                chunks.append(
                    Chunk(
                        document_id=document.document_id,
                        document_name=document.file_name,
                        chunk_id=chunk_id,
                        text=text
                    )
                )

                chunk_id += 1

            logger.info(
                "Chunking completed",
                extra={
                    "document": document.file_name,
                    "chunks": len(chunks)
                }
            )

            return chunks

        except Exception as error:

            logger.exception(
                str(error)
            )

            raise ChunkingException(
                str(error)
            )