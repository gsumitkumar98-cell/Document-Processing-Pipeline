from pathlib import Path

from src.models.document import Document

from src.interfaces.document_loader_interface import (
    DocumentLoaderInterface
)

from src.core.exceptions import (
    DocumentLoadException
)

from src.core.logger import get_logger


logger = get_logger(__name__)


class DocumentLoader(
    DocumentLoaderInterface
):

    def load(
        self,
        file_path: str
    ) -> Document:

        try:

            path = Path(
                file_path
            )

            if not path.exists():

                raise DocumentLoadException(
                    f"Document not found: {file_path}"
                )

            content = path.read_text(
                encoding="utf-8"
            )

            logger.info(
                "Document loaded",
                extra={
                    "file": path.name
                }
            )

            return Document(
                document_id=str(path),
                file_name=path.name,
                content=content
            )

        except Exception as error:

            logger.exception(
                str(error)
            )

            raise DocumentLoadException(
                str(error)
            )