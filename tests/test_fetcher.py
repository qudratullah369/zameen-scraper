import httpx
import pytest

from zameen_scraper.fetcher import fetch_html


def test_fetch_html_success(monkeypatch):
    class MockResponse:
        status_code = 200
        text = "<html><body>Zameen Property</body></html>"

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    result = fetch_html("https://www.zameen.com/Property/test.html")

    assert result == "<html><body>Zameen Property</body></html>"


def test_fetch_html_http_error(monkeypatch):
    class MockResponse:
        status_code = 404
        text = "Not Found"

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request("GET", "https://www.zameen.com/test"),
                response=httpx.Response(404),
            )

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_html("https://www.zameen.com/test")


def test_fetch_html_timeout(monkeypatch):
    def mock_get(*args, **kwargs):
        raise httpx.TimeoutException("Request timed out")

    monkeypatch.setattr(httpx, "get", mock_get)

    with pytest.raises(httpx.TimeoutException):
        fetch_html("https://www.zameen.com/test")
