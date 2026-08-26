from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from .models import PropertyListing


def _serialize_listing(listing: PropertyListing) -> dict:
    data = listing.model_dump()

    data["image_urls"] = " | ".join(listing.image_urls)
    data["property_features"] = " | ".join(listing.property_features)

    scraped_at = data.get("scraped_at")
    if isinstance(scraped_at, datetime):
        data["scraped_at"] = scraped_at.replace(tzinfo=None)

    return data


def export_listings(
    listings: list[PropertyListing],
    output_dir: str | Path = "output",
    filename: str = "zameen_listings",
) -> tuple[Path, Path]:
    """Export property listings to CSV and Excel."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_file = output_path / f"{filename}.csv"
    excel_file = output_path / f"{filename}.xlsx"

    rows = [_serialize_listing(listing) for listing in listings]

    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = list(PropertyListing.model_fields.keys())

    # CSV export
    with csv_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)

    # Excel export
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Listings"

    worksheet.append(fieldnames)

    for row in rows:
        worksheet.append(
            [row.get(field) for field in fieldnames]
        )

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(value))

        worksheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            60,
        )

    workbook.save(excel_file)

    return csv_file, excel_file
