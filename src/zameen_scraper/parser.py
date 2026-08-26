from __future__ import annotations
import json

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

    match = re.search(
        r"-(\d+)-\d+-\d+\.html(?:[?#].*)?$",
        url,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    match = re.search(
        r"/(?:Property/)?(\d+)(?:\.html)?/?(?:[?#].*)?$",
        url,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _extract_int(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def _extract_image_url(image) -> str | None:
    if image is None:
        return None

    for attr in ("src", "data-src", "data-lazy-src", "data-original"):
        value = image.get(attr)
        if value:
            return value.strip()

    srcset = image.get("srcset")
    if srcset:
        first = srcset.split(",")[0].strip()
        if first:
            return first.split()[0]

    return None


def _property_links(soup: BeautifulSoup):
    seen: set[str] = set()

    for link in soup.select('a[href*="/Property/"]'):
        href = link.get("href")
        if not href:
            continue

        property_id = _extract_property_id(href)
        if not property_id or property_id in seen:
            continue

        seen.add(property_id)
        yield link


def _find_listing_container(link):
    container = link

    for _ in range(8):
        if container.parent is None:
            break
        container = container.parent

        text = container.get_text(" ", strip=True)
        if len(text) > 60 and (
            "PKR" in text
            or "Crore" in text
            or "Lakh" in text
            or "Arab" in text
        ):
            return container

    return container


def _extract_price(text: str) -> str | None:
    match = re.search(
        r"PKR\s+[\d,.]+\s+(?:Crore|Lakh|Arab|Thousand)",
        text,
        re.IGNORECASE,
    )
    return match.group(0) if match else None


def _extract_area(text: str) -> str | None:
    match = re.search(
        r"\b\d+(?:\.\d+)?\s+(?:Marla|Kanal|Sq\.?\s*Ft|Square\s+Feet)",
        text,
        re.IGNORECASE,
    )
    return match.group(0) if match else None


def _extract_bedrooms_bathrooms(text: str) -> tuple[int | None, int | None]:
    beds = None
    baths = None

    m = re.search(r"\b(\d+)\s+Beds?\b", text, re.IGNORECASE)
    if m:
        beds = int(m.group(1))

    m = re.search(r"\b(\d+)\s+Baths?\b", text, re.IGNORECASE)
    if m:
        baths = int(m.group(1))

    if beds is not None or baths is not None:
        return beds, baths

    area_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s+(?:Marla|Kanal|Sq\.?\s*Ft|Square\s+Feet)\b",
        text,
        re.IGNORECASE,
    )
    if area_match:
        before = text[: area_match.start()]
        numbers = re.findall(r"\b(\d+)\b", before)
        if len(numbers) >= 2:
            return int(numbers[-2]), int(numbers[-1])

    return None, None


def _extract_location(text: str, price: str | None, area: str | None) -> str | None:
    if not price:
        return None

    after_price = text.split(price, 1)[-1].strip()

    if area:
        parts = re.split(
            rf"\b{re.escape(area)}\b",
            after_price,
            maxsplit=1,
            flags=re.IGNORECASE,
        )
        candidate = parts[0].strip() if parts else ""
    else:
        candidate = after_price

    if not candidate:
        return None

    candidate = re.sub(
        r"\bAdded:\s*.*$",
        "",
        candidate,
        flags=re.IGNORECASE,
    ).strip()

    candidate = re.sub(r"^[\s|]+|[\s|]+$", "", candidate)

    # Drop trailing bed/bath numbers (e.g. "Lahore 4 4" or "Lahore | 4 | 4")
    candidate = re.sub(r"(?:\s*\|\s*\d+){1,3}\s*$", "", candidate).strip()
    candidate = re.sub(r"(?:\s+\d+){1,3}\s*$", "", candidate).strip()

    candidate = re.sub(r"\s*\|\s*", ", ", candidate)
    candidate = re.sub(r"\s{2,}", " ", candidate).strip(" ,|")

    if candidate and len(candidate) < 180:
        return candidate

    return None


def _extract_agency_name(container, title: str | None) -> str | None:
    selectors = (
        ".agent-name",
        ".agency-name",
        "[class*='agency']",
        "[class*='agent']",
    )
    for selector in selectors:
        value = _text(container.select_one(selector))
        if value:
            return value

    if title:
        match = re.search(
            r'(?:Download the App|Contact|By)\s+[""]?(.+?)[""]?(?:[.\"\']|$)',
            title,
            re.IGNORECASE,
        )
        if match:
            value = match.group(1).strip(" \"'")
            if value and len(value) < 80:
                return value

        match = re.search(r'[""]([^""]{2,60})[""]', title)
        if match:
            return match.group(1).strip()

    return None


def _parse_real_listing(link) -> PropertyListing | None:
    href = link.get("href")
    property_id = _extract_property_id(href)
    if not property_id:
        return None

    listing_url = urljoin(BASE_URL, href)
    container = _find_listing_container(link)
    text = container.get_text(" ", strip=True)

    title = link.get("title")
    if title:
        title = title.strip()
    if not title:
        title = _text(container.select_one("h1, h2, h3"))
    if not title:
        title = _text(link)

    price = _extract_price(text)
    area = _extract_area(text)
    location = _extract_location(text, price, area)
    bedrooms, bathrooms = _extract_bedrooms_bathrooms(text)

    image_urls: list[str] = []
    for img in container.select("img"):
        url = _extract_image_url(img)
        if url and url not in image_urls:
            image_urls.append(url)

    agent_name = _text(container.select_one(".agent-name"))
    agency_name = _extract_agency_name(container, title)
    phone = _text(container.select_one(".phone"))
    email = _text(container.select_one(".email"))

    return PropertyListing(
        property_id=property_id,
        title=title,
        price=price,
        location=location,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        area=area,
        description=None,
        listing_url=listing_url,
        image_urls=image_urls,
        agent_name=agent_name,
        agency_name=agency_name,
        phone=phone,
        email=email,
    )


def parse_listing_card(html: str) -> PropertyListing:
    soup = BeautifulSoup(html, "lxml")

    card = soup.select_one("article.property-card")
    if card is None:
        card = soup

    link = card.select_one('a[href*="/Property/"]')
    if link is None:
        link = card.select_one("a[href]")

    href = link.get("href") if link else None
    listing_url = urljoin(BASE_URL, href) if href else None

    title = _text(card.select_one("h2, h3"))
    if not title and link:
        title = (link.get("title") or "").strip() or None

    price = _text(card.select_one(".price"))
    location = _text(card.select_one(".location"))
    description = _text(card.select_one(".description"))
    bedrooms = _extract_int(_text(card.select_one(".beds")))
    bathrooms = _extract_int(_text(card.select_one(".baths")))
    area = _text(card.select_one(".area"))
    agent_name = _text(card.select_one(".agent-name"))
    agency_name = _text(card.select_one(".agency-name"))
    phone = _text(card.select_one(".phone"))
    email = _text(card.select_one(".email"))

    image_urls: list[str] = []
    for img in card.select("img"):
        url = _extract_image_url(img)
        if url and url not in image_urls:
            image_urls.append(url)

    if link:
        parsed = _parse_real_listing(link)
        if parsed is not None:
            if description:
                parsed.description = description
            if agent_name:
                parsed.agent_name = agent_name
            if agency_name:
                parsed.agency_name = agency_name
            if phone:
                parsed.phone = phone
            if email:
                parsed.email = email
            if not parsed.image_urls and image_urls:
                parsed.image_urls = image_urls
            return parsed

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
        image_urls=image_urls,
        agent_name=agent_name,
        agency_name=agency_name,
        phone=phone,
        email=email,
    )


def parse_listing_page(html: str) -> list[PropertyListing]:
    soup = BeautifulSoup(html, "lxml")

    cards = soup.select("article.property-card")
    if cards:
        return [parse_listing_card(str(card)) for card in cards]

    listings: list[PropertyListing] = []
    for link in _property_links(soup):
        listing = _parse_real_listing(link)
        if listing is not None:
            listings.append(listing)

    return listings

def extract_phone_from_detail(detail_html: str) -> Dict[str, Optional[str]]:
    '''
    Extract phone numbers from Zameen property detail page.
    
    Looks for phoneNumber object in JSON data within script tags.
    
    Returns:
        Dict with keys: phone, whatsapp, mobile
        Example: {
            'phone': '+923007091498',
            'whatsapp': '923007091498',
            'mobile': '+923007091498'
        }
    '''
    result = {
        'phone': None,
        'whatsapp': None,
        'mobile': None
    }
    
    # Search for phoneNumber JSON pattern
    patterns = [
        r'"phoneNumber"\s*:\s*({[^}]+(?:{[^}]*}[^}]*)*})',
        r'"phoneNumber"\s*:\s*({[^}]+})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, detail_html)
        for match in matches:
            try:
                json_str = match.strip()
                json_str = json_str.replace('\\"', '"')
                phone_data = json.loads(json_str)
                
                if 'phone' in phone_data:
                    result['phone'] = phone_data['phone']
                if 'whatsapp' in phone_data:
                    result['whatsapp'] = phone_data['whatsapp']
                if 'mobile' in phone_data:
                    result['mobile'] = phone_data['mobile']
                    
                if 'mobileNumbers' in phone_data and phone_data['mobileNumbers']:
                    if not result['mobile']:
                        result['mobile'] = phone_data['mobileNumbers'][0]
                    if not result['phone']:
                        result['phone'] = phone_data['mobileNumbers'][0]
                        
                if any(result.values()):
                    return result
                    
            except json.JSONDecodeError:
                continue
    
    # Fallback: search for phone pattern in the page
    phone_patterns = [
        r'\+92\d{10}',
        r'92\d{10}',
        r'0[3-9]\d{9}',
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, detail_html)
        if matches:
            phone = matches[0]
            if phone.startswith('+'):
                result['phone'] = phone
                result['mobile'] = phone
            elif phone.startswith('92') and len(phone) == 12:
                result['phone'] = '+' + phone
                result['mobile'] = '+' + phone
                result['whatsapp'] = phone
            elif phone.startswith('0') and len(phone) == 11:
                result['phone'] = '+92' + phone[1:]
                result['mobile'] = '+92' + phone[1:]
                result['whatsapp'] = '92' + phone[1:]
            break
    
    return result

