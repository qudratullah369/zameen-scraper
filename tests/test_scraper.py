import httpx

from zameen_scraper.scraper import fetch_page


def test_fetch_page_success(monkeypatch):
    class MockResponse:
        status_code = 200
        text = "<html>Zameen Property</html>"

        def raise_for_status(self):
            pass

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get(self, url):
            assert url == "https://www.zameen.com/test"
            return MockResponse()

    monkeypatch.setattr(httpx, "Client", MockClient)

    status_code, html = fetch_page(
        "https://www.zameen.com/test"
    )

    assert status_code == 200
    assert html == "<html>Zameen Property</html>"


def test_fetch_page_http_error(monkeypatch):
    class MockResponse:
        status_code = 404
        text = "Not Found"

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request(
                    "GET",
                    "https://www.zameen.com/test",
                ),
                response=httpx.Response(404),
            )

    class MockClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "Client", MockClient)

    try:
        fetch_page("https://www.zameen.com/test")
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError("Expected HTTPStatusError")


def test_fetch_page_timeout(monkeypatch):
    class MockClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def get(self, url):
            raise httpx.TimeoutException("Request timed out")

    monkeypatch.setattr(httpx, "Client", MockClient)

    try:
        fetch_page("https://www.zameen.com/test")
    except httpx.TimeoutException:
        pass
    else:
        raise AssertionError("Expected TimeoutException")
import zameen_scraper.scraper as scraper


def test_scrape_listings(monkeypatch):
    html = """
    <html>
      <body>
        <article class="property-card">
          <a href="/Property/123456.html">
            <h2>5 Marla House</h2>
          </a>
          <div class="price">PKR 2.5 Crore</div>
          <div class="location">DHA Lahore</div>
          <div class="beds">4 Beds</div>
          <div class="baths">5 Baths</div>
          <div class="area">5 Marla</div>
          <div class="description">Beautiful house</div>
          <div class="agent-name">Ali Estate</div>
          <div class="phone">03001234567</div>
          <div class="email">agent@example.com</div>
        </article>
      </body>
    </html>
    """

    def mock_fetch_page(url, timeout=20.0):
        assert url == "https://www.zameen.com/Homes/Lahore-1-1.html"
        return 200, html

    monkeypatch.setattr(scraper, "fetch_page", mock_fetch_page)

    listings = scraper.scrape_listings("lahore")

    assert len(listings) == 1
    assert listings[0].property_id == "123456"
    assert listings[0].title == "5 Marla House"
    assert listings[0].phone == "03001234567"
    assert listings[0].email == "agent@example.com"
    assert listings[0].agent_name == "Ali Estate"
