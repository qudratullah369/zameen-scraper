from __future__ import annotations

import httpx

from .parser import parse_listing_page
from .search import build_search_url


BASE_URL = "https://www.zameen.com"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_page(
    url: str,
    timeout: float = 20.0,
) -> tuple[int, str]:
    """Fetch one public HTML page."""

    with httpx.Client(
        headers=DEFAULT_HEADERS,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = client.get(url)
        response.raise_for_status()

        return response.status_code, response.text


def scrape_listings(
    city: str,
    purpose: str | None = None,
    page: int | None = None,
    timeout: float = 20.0,
):
    """Fetch and parse property listings for a city."""

    url = build_search_url(
        city,
        purpose=purpose,
        page=page,
    )

    _, html = fetch_page(
        url,
        timeout=timeout,
    )

    return parse_listing_page(html)
