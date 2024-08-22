"""
This script crawls a website and saves the embeddings extracted from the text of each page to a text file.
"""
import re
import urllib.request
from collections import deque
from urllib.error import URLError
from urllib.parse import urlparse

from langchain_openai import OpenAIEmbeddings
import requests
from bs4 import BeautifulSoup

from langchain_community.vectorstores.mongodb_atlas import MongoDBAtlasVectorSearch
from src.context import AppContext
from src.application.embeddings.document_chunker import DocumentChunker
from src.application.embeddings.hyperlink_parser import HyperlinkParser

# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]*://.+"

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class EmbeddingGenerator(metaclass=SingletonMeta):
    """
    Class to generate embeddings for text data.
    """

    def __init__(self, app_context: AppContext):
        self.logger = app_context.logger
        mongodb_cluster_uri = app_context.env_vars.MONGODB_CLUSTER_URI
        embedding_api_key = app_context.env_vars.EMBEDDINGS_API_KEY
        configuration = app_context.configurations

        embedding = OpenAIEmbeddings(openai_api_key=embedding_api_key, model=configuration.embeddings.name)

        self._document_chunker = DocumentChunker(embedding=embedding)

        self._embedding_vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=mongodb_cluster_uri,
            namespace=f"{configuration.vectorStore.dbName}.{configuration.vectorStore.collectionName}",
            embedding=embedding,
            index_name=configuration.vectorStore.indexName,
            embedding_key=configuration.vectorStore.embeddingKey,
            relevance_score_fn=configuration.vectorStore.relevanceScoreFn,
            text_key=configuration.vectorStore.textKey
        )


    def _get_hyperlinks(self, url):
        """
        Function to get the hyperlinks from a URL
        """

        try:
            # Open the URL and read the HTML
            with urllib.request.urlopen(url) as response:
                # If the response is not HTML, return an empty list
                if not response.info().get("Content-Type").startswith("text/html"):
                    return []

                html = response.read().decode("utf-8")
        except URLError as e:
            self.logger.error(e)
            return []

        # Create the HTML Parser and then Parse the HTML to get hyperlinks
        parser = HyperlinkParser()
        parser.feed(html)

        return parser.hyperlinks


    def _get_domain_hyperlinks(self, local_domain: str, url: str):
        """
        Function to get the hyperlinks from a URL that are within the same domain
        
        Args:
            local_domain (str): The domain to compare the hyperlinks against.
            url (str): The URL to extract hyperlinks from.
        
        Returns:
            list: A list of hyperlinks that are within the same domain.
        """
        clean_links = []
        for link in set(self._get_hyperlinks(url)):
            clean_link = None

            # If the link is a URL, check if it is within the same domain
            if re.search(HTTP_URL_PATTERN, link):
                # Parse the URL and check if the domain is the same
                url_obj = urlparse(link)
                # Link should be within the same domain and should start with one of the paths
                if url_obj.netloc == local_domain:
                    clean_link = link

            # If the link is not a URL, check if it is a relative link
            else:
                if link.startswith("/"):
                    link = link[1:]
                elif link.startswith("#") or link.startswith("mailto:"):
                    continue
                clean_link = "https://" + local_domain + "/" + link

            if clean_link is not None:
                if clean_link.endswith("/"):
                    clean_link = clean_link[:-1]
                clean_links.append(clean_link)

        return list(set(clean_links))
    
    def crawl(self, url: str):
        """
        Crawls the given URL and saves the text content of each page to a text file.

        Args:
            url (str): The URL to crawl.

        Returns:
            None
        """

        local_domain = urlparse(url).netloc

        queue = deque([url])
        seen = set([url])

        # While the queue is not empty, continue crawling
        while queue:
            # Get the next URL from the queue
            url = queue.pop()
            self.logger.debug(f"Crawling page: {url}")  # for debugging and to see the progress

            # Get the text from the URL using BeautifulSoup
            soup = BeautifulSoup(requests.get(url, timeout=5).text, "html.parser")

            # Get the text but remove the tags
            text = soup.get_text()

            # If the crawler gets to a page that requires JavaScript, it will stop the crawl
            if "You need to enable JavaScript to run this app." in text:
                self.logger.debug(
                    "Unable to parse page " + url + " due to JavaScript being required"
                )
                continue

            chunks = self._document_chunker.split_text_into_chunks(text=text, url=url)
            self.logger.debug(f"Extracted {len(chunks)} chunks from the page. Generated embeddings for these...")  # for debugging and to see the progress
            self._embedding_vector_store.add_documents(chunks)
            self.logger.debug("Embeddings generation completed. Extracting links...")  # for debugging and to see the progress

            hyperlinks = self._get_domain_hyperlinks(local_domain, url)
            if len(hyperlinks) == 0:
                self.logger.debug("No links found, move on.")

            # Get the hyperlinks from the URL and add them to the queue
            for link in hyperlinks:
                if link not in seen:
                    self.logger.debug(f"Found new link: {link}")
                    queue.append(link)
                    seen.add(link)

        self.logger.debug("Crawling completed.")
