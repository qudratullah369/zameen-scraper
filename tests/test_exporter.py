from zameen_scraper.exporter import export_listings
from zameen_scraper.models import PropertyListing


def test_export_listings_creates_csv_and_excel(tmp_path):
    listings = [
        PropertyListing(
            property_id="54647215",
            title="5 Marla Luxury House",
            price="PKR 2.6 Crore",
            location="DHA 9 Town",
            bedrooms=4,
            bathrooms=5,
            phone="+923007091498",
            whatsapp="923007091498",
            listing_url="https://www.zameen.com/Property/test-54647215-1-1.html",
            image_urls=["https://example.com/1.jpg", "https://example.com/2.jpg"],
            property_features=["Parking", "Electricity"],
        )
    ]

    csv_file, excel_file = export_listings(
        listings,
        output_dir=tmp_path,
        filename="zameen_lahore",
    )

    assert csv_file.exists()
    assert excel_file.exists()

    assert csv_file.suffix == ".csv"
    assert excel_file.suffix == ".xlsx"

    csv_text = csv_file.read_text(encoding="utf-8")

    assert "54647215" in csv_text
    assert "5 Marla Luxury House" in csv_text
    assert "+923007091498" in csv_text
    assert "923007091498" in csv_text
    assert "https://example.com/1.jpg | https://example.com/2.jpg" in csv_text
    assert "Parking | Electricity" in csv_text
