from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import PropertyListing


BASE_URL = "https://www.zameen.com"


def _text(element) -> str | None:
    if element is None:
        return None

    value = element.get_text(" ", strip=True)
    return value or None


def _extract_property_id(url: str | None) -> str | None:
    if not url:
        return None

    match = re.search(r"/(?:Property/)?(\d+)(?:\.html)?/?$", url)
    return match.group(1) if match else None


def _extract_int(value: str | None) -> int | None:
    if not value:
        return None

    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def parse_listing_card(html: str) -> PropertyListing:
    """Parse one property listing card from HTML."""

    soup = BeautifulSoup(html, "lxml")

    card = soup.select_one("article.property-card")
    if card is None:
        card = soup

    link = card.select_one("a[href]")
    href = link.get("href") if link else None

    listing_url = urljoin(BASE_URL, href) if href else None

    title = _text(card.select_one("h2"))
    price = _text(card.select_one(".price"))
    location = _text(card.select_one(".location"))
    description = _text(card.select_one(".description"))

    bedrooms = _extract_int(_text(card.select_one(".beds")))
    bathrooms = _extract_int(_text(card.select_one(".baths")))
    area = _text(card.select_one(".area"))

    return PropertyListing(
        property_id=_extract_property_id(href),
        title=title,
        price=price,
        location=location,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area=area,
        description=description,
        listing_url=listing_url,
    )
