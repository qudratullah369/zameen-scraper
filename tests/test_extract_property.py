from pathlib import Path

import pytest

from extract_property import extract_property_data


SAMPLE_HTML = r'''
<html>
<body>
<script>
{
    "externalID": "12345678",
    "title": "Beautiful 1 Kanal House For Sale",
    "price": 95000000,
    "purpose": "for-sale",
    "rooms": 5,
    "baths": 6,
    "description": "Beautiful house\u003Cbr\u003EPrime location",
    "contactName": "Test Agent",
    "agency": "Test Agency",
    "phoneNumber": {
        "mobileNumbers": ["+923001234567"],
        "phoneNumbers": [],
        "whatsapp": "923001234567"
    },
    "photoCount": 2,
    "photos": [
        {"url": "https:\\/\\/example.com\\/photo1.jpg"},
        {"url": "https:\\/\\/example.com\\/photo2.jpg"}
    ]
}
</script>

<div aria-label="Type">House</div>
<div aria-label="Area"><span>1 Kanal</span></div>
<div aria-label="Location">DHA Phase 6, Lahore</div>
</body>
</html>
'''


def test_extract_property_data(tmp_path):
    html_file = tmp_path / "property.html"
    html_file.write_text(SAMPLE_HTML, encoding="utf-8")

    result = extract_property_data(html_file)

    assert result["property_id"] == "12345678"
    assert result["title"] == "Beautiful 1 Kanal House For Sale"
    assert result["property_type"] == "House"
    assert result["price"] == 95000000
    assert result["purpose"] == "Buy"
    assert result["area"] == "1 Kanal"
    assert result["bedrooms"] == 5
    assert result["bathrooms"] == 6
    assert result["location"] == "DHA Phase 6, Lahore"
    assert result["agent"] == "Test Agent"
    assert result["agency"] == "Test Agency"
    assert result["mobile"] == "+923001234567"
    assert result["whatsapp"] == "923001234567"
    assert result["photo_count"] == 2
    assert len(result["photos"]) == 2


def test_extract_property_data_detects_property_id(tmp_path):
    html = SAMPLE_HTML.replace("12345678", "98765432")

    html_file = tmp_path / "property.html"
    html_file.write_text(html, encoding="utf-8")

    result = extract_property_data(html_file)

    assert result["property_id"] == "98765432"


def test_extract_property_data_missing_property_id(tmp_path):
    html_file = tmp_path / "property.html"
    html_file.write_text(
        '<html><body><div>No property ID</div></body></html>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Property externalID not found"):
        extract_property_data(html_file)
