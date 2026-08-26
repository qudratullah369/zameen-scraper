from __future__ import annotations

from urllib.parse import urlencode


BASE_URL = "https://www.zameen.com"


def build_search_url(
    city: str,
    purpose: str | None = None,
    page: int | None = None,
) -> str:
    """Build a Zameen.com property search URL."""

    city = city.strip()

    if not city:
        raise ValueError("City is required")

    city_slug = city.replace(" ", "-").title()

    if purpose == "for-sale":
        url = f"{BASE_URL}/Homes/{city_slug}-1-1.html"
    elif purpose == "for-rent":
        url = f"{BASE_URL}/Homes/{city_slug}-1-2.html"
    else:
        url = f"{BASE_URL}/Homes/{city_slug}-1-1.html"

    if page is not None:
        if page < 1:
            raise ValueError("Page must be >= 1")

        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{urlencode({'page': page})}"

    return url
