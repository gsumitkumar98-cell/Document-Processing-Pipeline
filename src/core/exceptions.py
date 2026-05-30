class PipelineException(
    Exception
):
    """
    Base Exception
    """

    pass


class DocumentLoadException(
    PipelineException
):
    """
    Document Loading Error
    """

    pass


class ChunkingException(
    PipelineException
):
    """
    Chunk Creation Error
    """

    pass


class RepositoryException(
    PipelineException
):
    """
    Repository Error
    """

    pass


class RetrievalException(
    PipelineException
):
    """
    Search Error
    """

    pass