class UnsupportedLlmProviderError(Exception):
    """Exception raised for errors during the creation of the LLM class for a specific provider."""

    def __init__(self, provider_type: str):
        super().__init__(f"Provider \"{provider_type}\" for LLM is not supported.")
