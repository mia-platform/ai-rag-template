from src.application.embeddings.hyperlink_parser import HyperlinkParser


def test_initial_hyperlinks_empty():
    parser = HyperlinkParser()
    assert not parser.hyperlinks

def test_handle_starttag_adds_hyperlink():
    parser = HyperlinkParser()
    parser.handle_starttag('a', [('href', 'http://example.com')])
    assert parser.hyperlinks == ['http://example.com']

def test_handle_starttag_ignores_non_anchor_tags():
    parser = HyperlinkParser()
    parser.handle_starttag('div', [('href', 'http://example.com')])
    assert not parser.hyperlinks

def test_handle_starttag_ignores_anchor_without_href():
    parser = HyperlinkParser()
    parser.handle_starttag('a', [('class', 'link')])
    assert not parser.hyperlinks

def test_handle_starttag_multiple_hyperlinks():
    parser = HyperlinkParser()
    parser.handle_starttag('a', [('href', 'http://example1.com')])
    parser.handle_starttag('a', [('href', 'http://example2.com')])
    assert parser.hyperlinks == ['http://example1.com', 'http://example2.com']
