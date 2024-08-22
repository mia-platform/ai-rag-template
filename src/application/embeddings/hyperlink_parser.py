"""
Module providing the HyperlinkParser class.
"""

from html.parser import HTMLParser


class HyperlinkParser(HTMLParser):
    """
    A class that parses HTML and extracts hyperlinks.

    Attributes:
        hyperlinks (list): A list to store the extracted hyperlinks.

    Methods:
        handle_starttag(tag, attrs): Overrides the HTMLParser's handle_starttag method to extract hyperlinks.
    """

    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])
