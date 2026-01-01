import re
from collections import deque
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch

from src.application.embeddings.document_chunker import DocumentChunker
from src.application.embeddings.hyperlink_parser import HyperlinkParser
from src.context import AppContext
from src.infrastracture.embeddings_manager.embeddings_manager import EmbeddingsManager

# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]*://.+"


class EmbeddingsService:
    """
    Class to generate embeddings for text data.
    """

    def __init__(self, app_context: AppContext):
        self.logger = app_context.logger
        mongodb_cluster_uri = app_context.env_vars.MONGODB_CLUSTER_URI
        configuration = app_context.configurations

        embedding = EmbeddingsManager(app_context).get_embeddings_instance()

        self._document_chunker = DocumentChunker(embedding=embedding)

        self._embedding_vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=mongodb_cluster_uri,
            namespace=f"{configuration.vectorStore.dbName}.{configuration.vectorStore.collectionName}",
            embedding=embedding,
            index_name=configuration.vectorStore.indexName,
            embedding_key=configuration.vectorStore.embeddingKey,
            relevance_score_fn=configuration.vectorStore.relevanceScoreFn,
            text_key=configuration.vectorStore.textKey,
        )

    def _get_hyperlinks(self, raw_text: str):
        """
        Function to get the hyperlinks from a raw HTML text
        """
        # Create the HTML Parser and then Parse the HTML to get hyperlinks
        parser = HyperlinkParser()
        parser.feed(raw_text)

        return parser.hyperlinks

    def _get_domain_hyperlinks(self, raw_text: str, local_domain: str, path: str | None = None):
        """
        Function to get the hyperlinks from a URL that are within the same domain

        Args:
            raw_text (str): The raw HTML text to extract hyperlinks from.
            local_domain (str): The domain to compare the hyperlinks against.

        Returns:
            list: A list of hyperlinks that are within the same domain.
        """
        clean_links = []
        for link in set(self._get_hyperlinks(raw_text)):
            clean_link = None

            # If the link is a URL, check if it is within the same domain
            if re.search(HTTP_URL_PATTERN, link):
                # Parse the URL and check if the domain is the same
                url_obj = urlparse(link)
                # Link should be within the same domain and should start with one of the paths
                if url_obj.netloc == local_domain and url_obj.path.startswith(path or ""):
                    clean_link = link

            # If the link is not a URL, check if it is a relative link
            else:
                if link.startswith("/"):
                    link = link[1:]  # noqa: PLW2901
                elif link.startswith("#") or link.startswith("mailto:"):
                    continue
                clean_link = "https://" + local_domain + "/" + link

            if clean_link is not None:
                if clean_link.endswith("/"):
                    clean_link = clean_link[:-1]
                if path:
                    # Check if the link starts with the path (if included)
                    url_obj = urlparse(clean_link)
                    if not url_obj.path.startswith(path or ""):
                        continue
                clean_links.append(clean_link)

        return list(set(clean_links))

    def generate_from_url(self, url: str, filter_path: str | None = None):
        """
        Crawls the given URL and saves the text content of each page to a text file.

        Args:
            url (str): The URL to crawl. From this URL, the crawler will extract the text content
                of said page and any other page connected via hyperlinks (anchor tags).
            domain (str | None, optional): The domain to compare the hyperlinks against. If None,
                the hyperlinks will not be filtered by domain. Defaults to None.

        Returns:
            None
        """

        local_domain = urlparse(url).netloc
        path = urlparse(filter_path).path if filter_path else None

        queue = deque([url])
        seen = {url}

        # While the queue is not empty, continue crawling
        while queue:
            # Get the next URL from the queue
            url = queue.pop()
            self.logger.debug(f"Scraping page: {url}")  # for debugging and to see the progress

            # Get the text from the URL using BeautifulSoup
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            # check the response headers to see if the content is HTML
            if not response.headers.get("Content-Type", "").startswith("text/html"):
                self.logger.debug(f"Skipping page {url} as it is not HTML content.")
                continue

            raw_text = response.text

            # Get the text but remove the tags
            soup = BeautifulSoup(raw_text, "html.parser")
            text = soup.get_text()

            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if "You need to enable JavaScript to run this app." in text:
                self.logger.debug(f"Unable to parse page {url} due to JavaScript being required")
                continue

            chunks = self._document_chunker.split_text_into_chunks(text=text, url=url)
            self.logger.debug(f"Extracted {len(chunks)} chunks from the page. Generated embeddings for these...")
            self._embedding_vector_store.add_documents(chunks)

            self.logger.debug("Embeddings generation completed. Extracting links...")
            hyperlinks = self._get_domain_hyperlinks(raw_text, local_domain, path)
            if len(hyperlinks) == 0:
                self.logger.debug("No links found, move on.")

            # Get the hyperlinks from the URL and add them to the queue
            for link in hyperlinks:
                if link not in seen:
                    self.logger.debug(f"Found new link: {link}")
                    queue.append(link)
                    seen.add(link)

        self.logger.debug("Scraping completed.")

    def generate_from_text(self, text: str):
        """
        Take the string passed as argument, it separates the text into chunks and generates embeddings for each chunk.

        Args:
            text (str): The text to generate embeddings for.

        Returns:
            None
        """
        chunks = self._document_chunker.split_text_into_chunks(text=text)
        self.logger.debug(f"Extracted {len(chunks)} chunks from the page. Generated embeddings for these...")
        self._embedding_vector_store.add_documents(chunks)
        self.logger.debug("Embeddings generation completed.")
