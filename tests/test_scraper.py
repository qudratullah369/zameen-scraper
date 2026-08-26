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
