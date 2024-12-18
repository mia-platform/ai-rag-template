"""
Module to include the EmbeddingGenerator class, a class that generates embeddings for text data.
"""

import hashlib
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker


class DocumentChunker():
    """
    Initialize the DocumentChunker class.
    """

    def __init__(self, embedding: Embeddings) -> None:
        self._chunker = SemanticChunker(embeddings=embedding, breakpoint_threshold_type='percentile')

    def _remove_consecutive_newlines(self, text: str) -> str:
        """
        Remove duplicate newlines from the text.
        """
        return "\n".join([line for line in text.split("\n\n") if line.strip()])

    def _generate_sha(self, content: str) -> str:
        """
        Generate a SHA hash for the given content.
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def split_text_into_chunks(self, text: str, url: str | None = None) -> List[Document]:
        """
        Generate chunks via semantic separation from a given text

        Args:
            text (str): The input text.
            url (str | None): The URL of the text. Could be None if the text is not from a URL (e.g. from an uploaded file).
        """
        content = self._remove_consecutive_newlines(text)
        sha = self._generate_sha(content)

        metadata = {"sha": sha}
        if url:
            metadata["url"] = url

        document = Document(page_content=content, metadata=metadata)
        chunks = [Document(page_content=chunk) for chunk in self._chunker.split_text(document.page_content)]
        # NOTE: "copy" method actually exists.
        # pylint: disable=E1101
        return [Document(page_content=chunk.page_content, metadata=document.metadata.copy()) for chunk in chunks]
