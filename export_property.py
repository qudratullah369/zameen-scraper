from pathlib import Path
import csv
import json

from extract_property import extract_property_data


INPUT_FILE = "output/property_54663983.html"
OUTPUT_DIR = Path("output")


def export_property(file_path):
    data = extract_property_data(file_path)

    OUTPUT_DIR.mkdir(exist_ok=True)

    property_id = data.get("property_id", "unknown")

    # JSON
    json_file = OUTPUT_DIR / f"property_{property_id}.json"

    with json_file.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    # CSV
    csv_file = OUTPUT_DIR / f"property_{property_id}.csv"

    csv_data = data.copy()

    # Photos ko CSV mein ek field mein rakhenge
    csv_data["photos"] = " | ".join(data.get("photos", []))

    with csv_file.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=csv_data.keys()
        )

        writer.writeheader()
        writer.writerow(csv_data)

    print("EXPORT SUCCESS")
    print(f"JSON: {json_file}")
    print(f"CSV : {csv_file}")


if __name__ == "__main__":
    export_property(INPUT_FILE)
