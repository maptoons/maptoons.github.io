import os

from dotenv import load_dotenv

from directory import BusinessDirectory
from utils import load_json


class DataSource:
    def __init__(self, name: str, geojson: str, url: str  = "", csv: str  = ""):
        self.name = name
        self.geojson = geojson
        self.url = url
        self.csv = csv


class Corrections:
    def __init__(self, filename: str, corrections: str = "", csv: str = "", img: str = ""):
        self.filename = filename
        self.corrections = corrections
        self.csv = csv
        self.img = img


def main():
    # 1. Load external data
    load_dotenv() # API key for geocoder
    census_places = load_json("data/us_census/ny_places_poly.geojson")
    business_categories = load_json("data/subcategories.json")

    # 2. Scrape selected map urls
    print("\nCollecting business data from web for selected locations:")

    maps_to_scrape = [
        DataSource(
            name="Hicksville, NY",
            url="https://maptoons.com/hicksville-2025.html",
            geojson="data/hicksville.geojson",
        ),
        DataSource(
            name="Long Beach, NY",
            csv="data/2025_Best_of_Long_Beach.csv",
            geojson="data/long_beach.geojson",
        )
    ]
    for m in maps_to_scrape:
        print(m.name, m.url, m.csv)
        if not os.path.isfile(m.geojson):
            map_data = BusinessDirectory(m.name)
            if m.url:
                map_data.scrape(m.url)
            elif m.csv:
                map_data.load_csv(m.csv)
            map_data.match_categories(business_categories)
            map_data.match_towns(census_places)
            map_data.geocode()
            map_data.save_geojson(m.geojson)
        else:
            print("  Skipping download.", m.geojson, "already exists")

    # 3. Apply local corrections
    print("\nApplying updates/corrections:")
    maps_to_fix = [
        Corrections(
            filename="data/hicksville.geojson",
            corrections="data/hicksville-corrections.geojson",
            csv="data/Best_of_HK_2024.csv",
            img="img/HK-*png",
        ),
        Corrections(
            filename="data/long_beach.geojson",
            corrections="data/long_beach-corrections.geojson",
            img="img/LB-*png"
        ),
    ]
    for m in maps_to_fix:
        print(m.filename)
        map_data = BusinessDirectory()
        map_data.load_geojson(m.filename)
        map_data.match_categories(business_categories)
        if m.csv:
            map_data.load_loc_from_csv(m.csv)
        if m.img:
            map_data.load_img(m.img)
        if m.corrections:
            map_data.load_geojson(m.corrections, keep_name=True)
        map_data.save_geojson(m.filename)


if __name__ == "__main__":
    main()
