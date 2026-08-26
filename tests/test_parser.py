from zameen_scraper.parser import parse_listing_card


SAMPLE_HTML = """
<article class="property-card">
    <a href="/Property/12345.html">
        <h2>A Beautiful House For Sale</h2>
    </a>

    <div class="price">PKR 2.5 Crore</div>
    <div class="location">DHA Phase 6, Lahore</div>

    <span class="beds">5</span>
    <span class="baths">6</span>
    <span class="area">1 Kanal</span>

    <p class="description">
        Beautiful house in prime location.
    </p>
</article>
"""


MINIMAL_HTML = """
<article class="property-card">
    <a href="/Property/99999.html">
        <h2>Small Property</h2>
    </a>
</article>
"""


INVALID_ID_HTML = """
<article class="property-card">
    <a href="/Property/abc.html">
        <h2>Property Without Numeric ID</h2>
    </a>
</article>
"""


def test_parse_listing_card():
    listing = parse_listing_card(SAMPLE_HTML)

    assert listing.title == "A Beautiful House For Sale"
    assert listing.property_id == "12345"
    assert listing.price == "PKR 2.5 Crore"
    assert listing.location == "DHA Phase 6, Lahore"
    assert listing.bedrooms == 5
    assert listing.bathrooms == 6
    assert listing.area == "1 Kanal"
    assert listing.description == "Beautiful house in prime location."
    assert listing.listing_url == "https://www.zameen.com/Property/12345.html"


def test_parse_listing_card_with_missing_optional_fields():
    listing = parse_listing_card(MINIMAL_HTML)

    assert listing.title == "Small Property"
    assert listing.property_id == "99999"
    assert listing.price is None
    assert listing.location is None
    assert listing.bedrooms is None
    assert listing.bathrooms is None
    assert listing.area is None


def test_parse_listing_card_with_invalid_property_id():
    listing = parse_listing_card(INVALID_ID_HTML)

    assert listing.title == "Property Without Numeric ID"
    assert listing.property_id is None
    assert listing.listing_url == "https://www.zameen.com/Property/abc.html"
