from pathlib import Path
import json
import re
import html as html_lib


def extract_property_data(file_path):
    html = Path(file_path).read_text(encoding="utf-8")

    # ---------------------------------------------------------
    # Find the main property JSON object using its unique ID
    # ---------------------------------------------------------
    property_id_match = re.search(
        r'"externalID"\s*:\s*"?(54663983)"?',
        html
    )

    if not property_id_match:
        raise ValueError("Property externalID not found")

    property_id = property_id_match.group(1)

    # Find the beginning of the property object around externalID.
    # We use the nearby "objectID" / property data region.
    object_start = html.rfind("{", 0, property_id_match.start())

    if object_start == -1:
        raise ValueError("Property object start not found")

    # ---------------------------------------------------------
    # Helper: extract a JSON string value after a given position
    # ---------------------------------------------------------
    def get_string(key, start=0, default=None):
        pattern = rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"'
        match = re.search(pattern, html[start:], re.DOTALL)

        if not match:
            return default

        try:
            return json.loads('"' + match.group(1) + '"')
        except json.JSONDecodeError:
            return match.group(1)

    def get_number(key, start=0, default=None):
        pattern = rf'"{re.escape(key)}"\s*:\s*(\d+(?:\.\d+)?)'
        match = re.search(pattern, html[start:], re.DOTALL)

        if not match:
            return default

        value = match.group(1)

        return int(value) if "." not in value else float(value)

    # ---------------------------------------------------------
    # Property details
    # ---------------------------------------------------------

    title = get_string("title", property_id_match.start())

    property_type_match = re.search(
        r'aria-label="Type">\s*([^<]+)',
        html
    )
    property_type = (
        property_type_match.group(1).strip()
        if property_type_match
        else None
    )

    price = get_number("price", property_id_match.start())

    purpose_raw = get_string("purpose", property_id_match.start())

    purpose = {
        "for-sale": "Buy",
        "for-rent": "Rent",
    }.get(purpose_raw, purpose_raw)

    rooms = get_number("rooms", property_id_match.start())

    baths = get_number("baths", property_id_match.start())

    # ---------------------------------------------------------
    # Area
    # ---------------------------------------------------------

    area_match = re.search(
        r'aria-label="Area">\s*<span>\s*([^<]+)',
        html
    )

    area = (
        area_match.group(1).strip()
        if area_match
        else None
    )

    # ---------------------------------------------------------
    # Location
    # ---------------------------------------------------------

    location_match = re.search(
        r'aria-label="Location">\s*([^<]+)',
        html
    )

    location = (
        location_match.group(1).strip()
        if location_match
        else None
    )

    # ---------------------------------------------------------
    # Description
    # ---------------------------------------------------------

    description = get_string(
        "description",
        property_id_match.start()
    )

    if description:
        description = html_lib.unescape(description)
        description = description.replace(
            r"\u003Cbr\u003E",
            "\n"
        )
        description = description.replace(
            r"\u003Cbr \u002F\u003E",
            "\n"
        )
        description = re.sub(
            r'<br\s*/?>',
            '\n',
            description,
            flags=re.I
        )
        description = re.sub(
            r'<[^>]+>',
            '',
            description
        )
        description = description.strip()

    # ---------------------------------------------------------
    # Agent
    # ---------------------------------------------------------

    agent = get_string(
        "contactName",
        property_id_match.start()
    )

    # ---------------------------------------------------------
    # Agency
    # ---------------------------------------------------------

    agency = get_string(
        "agency",
        property_id_match.start()
    )

    # If agency is stored as an object, find its name.
    if agency is None:
        agency_name_match = re.search(
            r'"agency"\s*:\s*\{.*?"name"\s*:\s*"((?:\\.|[^"\\])*)"',
            html[property_id_match.start():],
            re.DOTALL
        )

        if agency_name_match:
            try:
                agency = json.loads(
                    '"' + agency_name_match.group(1) + '"'
                )
            except json.JSONDecodeError:
                agency = agency_name_match.group(1)

    # ---------------------------------------------------------
    # Phone numbers
    # ---------------------------------------------------------

    phone_block_match = re.search(
        r'"phoneNumber"\s*:\s*\{(.*?)\}',
        html[property_id_match.start():],
        re.DOTALL
    )

    phone = None
    mobile = None
    whatsapp = None

    if phone_block_match:
        phone_block = phone_block_match.group(1)

        mobile_match = re.search(
            r'"mobileNumbers"\s*:\s*\[\s*"([^"]+)"',
            phone_block
        )

        phone_match = re.search(
            r'"phoneNumbers"\s*:\s*\[\s*"([^"]+)"',
            phone_block
        )

        whatsapp_match = re.search(
            r'"whatsapp"\s*:\s*"([^"]+)"',
            phone_block
        )

        if mobile_match:
            mobile = mobile_match.group(1)

        if phone_match:
            phone = phone_match.group(1)

        if not phone:
            phone = mobile

        if whatsapp_match:
            whatsapp = whatsapp_match.group(1)

    # ---------------------------------------------------------
    # Photo count
    # ---------------------------------------------------------

    photo_count = get_number(
        "photoCount",
        property_id_match.start(),
        0
    )

    # ---------------------------------------------------------
    # Photo URLs
    # ---------------------------------------------------------

    photos = []

    photo_pattern = (
        r'"photos"\s*:\s*\[(.*?)\]'
    )

    photo_match = re.search(
        photo_pattern,
        html[property_id_match.start():],
        re.DOTALL
    )

    if photo_match:
        photo_block = photo_match.group(1)

        photo_urls = re.findall(
            r'"url"\s*:\s*"([^"]+)"',
            photo_block
        )

        for url in photo_urls:
            url = url.replace(r'\u002F', '/')
            photos.append(url)

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    result = {
        "property_id": property_id,
        "title": title,
        "property_type": property_type,
        "price": price,
        "purpose": purpose,
        "area": area,
        "bedrooms": rooms,
        "bathrooms": baths,
        "location": location,
        "description": description,
        "agent": agent,
        "agency": agency,
        "phone": phone,
        "mobile": mobile,
        "whatsapp": whatsapp,
        "photo_count": photo_count,
        "photos": photos,
    }

    return result


if __name__ == "__main__":
    file_path = "output/property_54663983.html"

    result = extract_property_data(file_path)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
