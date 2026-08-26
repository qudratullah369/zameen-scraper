from zameen_scraper.search import build_search_url


def test_build_search_url_basic():
    url = build_search_url("lahore")

    assert url == "https://www.zameen.com/Homes/Lahore-1-1.html"


def test_build_search_url_for_sale():
    url = build_search_url("lahore", purpose="for-sale")

    assert url == "https://www.zameen.com/Homes/Lahore-1-1.html"


def test_build_search_url_with_page():
    url = build_search_url("lahore", page=2)

    assert "page=2" in url
