class UnsupportedEmbeddingsProviderError(Exception):
    """Exception raised for errors during the creation of the Embeddings class for a specific provider."""

    def __init__(self, provider_type: str):
        super().__init__(f"Provider \"{provider_type}\" for Embeddings is not supported.")
