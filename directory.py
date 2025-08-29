import csv
import re
import glob
from typing import Any, Dict
from pathlib import Path

from bs4 import BeautifulSoup

from feature import Business, Feature, Location
from utils import load_json, make_geojson, scrape_html


class FeatureDirectory:
    def __init__(self, name: str = ""):
        self.name = name
        self.features: Dict[str, Feature] = {}

    def load_geojson(self, filename: str, obj_type=Feature, keep_name = False):
        geo_json = load_json(filename)
        name = geo_json["name"]
        if name and not keep_name:
            self.name = name
        for feature in geo_json["features"]:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            feature_id = properties.get("id", None)
            if feature_id:
                if feature_id in self.features:
                    self.features[feature_id].update(properties, geometry)
                else:
                    self.features[feature_id] = obj_type(properties, geometry)


    def save_geojson(self, filename: str):
        features = [item.feature for item in self.features.values()]
        make_geojson(self.name, features, filename)


class LocationDirectory(FeatureDirectory):
    def __init__(self, name: str, census_places: Dict[str, Any]):
        super().__init__(name)
        self.census_places = census_places

    def scrape(self, url: str, root_tag=["div", "content"], target_tag=["article"]):
        last_update: Dict[str, int] = {}
        locations: Dict[str, Location] = {}

        print(f"Processing: {url}")
        parse_tree: BeautifulSoup = scrape_html(url, root_tag)
        for node in parse_tree.find_all(*target_tag):
            loc = Location()
            loc.load_html(node)
            loc_name = loc.properties.get("name")
            loc_year = loc.properties.get("year")
            if loc_name not in last_update or loc_year > last_update[loc_name]:
                print(f"  {loc_name}")
                last_update[loc_name] = loc_year
                locations[loc_name] = loc

        self.features.update(locations)
    
    def process(self):
        for location in self.features.values():
            location.bounding_box(self.census_places)


class BusinessDirectory(FeatureDirectory):
    def __init__(self, name: str = ""):
        super().__init__(name)

    def scrape(self, url: str, root_tag=["body"], target_tag=["div", "gear"]):
        parse_tree: BeautifulSoup = scrape_html(url, root_tag)
        for node in parse_tree.find_all(*target_tag):
            node_id = node["id"]
            business = Business()
            business.load_html(node)
            # business.scrape_favico(folder="data/logos")
            self.features[node_id] = business

    def load_csv(self, filename: str):
        with open(filename, "r") as f:
            for row in csv.DictReader(f):
                business = Business()
                business.load_csv(row)
                b_id = business.properties.get("id")
                self.features[b_id] = business

    def load_loc_from_csv(self, filename: str):
        name_map: Dict[str,int] = {}
        phone_map: Dict[str,int] = {}
        addr_map: Dict[str,int] = {}
        with open(filename, "r") as f:
            for row in csv.DictReader(f):
                loc = int(re.search(r"\d+", row["LOC"]).group())
                name = row["Business"]
                phone = row["Phone"]
                addr = row["Address"]
                if addr:
                    addr_ = addr[:-1] if addr[-1] == "." else addr + "."
                    addr_map[addr_] = loc
                    addr_map[addr] = loc
                name_map[name] = loc
                phone_map[phone] = loc
        
        for feature in self.features.values():
            feature_name = feature.properties.get("mapname", None)
            feature_phone = feature.properties.get("phone", None)
            feature_addr = feature.properties.get("address", None)
            if feature_name and feature_name in name_map:
                loc = name_map[feature_name]
            elif feature_phone and feature_phone in phone_map:
                loc = phone_map[feature_phone]
            elif feature_addr and feature_addr in addr_map:
                loc = addr_map[feature_addr]
            else:
                continue # skip feature if we can't match by name, phone or address
            properties = {}
            properties["loc"] = loc
            feature.update(properties=properties)

    def load_img(self, pattern: str):
        loc_map = {}
        for input_path in glob.glob(pattern):
            file_stem = Path(input_path).stem
            file_id = file_stem.split("-")[-1]
            try:
                loc = int(re.search(r"\d+", file_id).group())
                priority = re.search(r"[a-zA-Z]+", file_id).group()
                loc_map[loc] = (priority, file_stem)
            except AttributeError as e:
                print("Error processing", file_stem, e)

        for feature in self.features.values():
            loc = feature.properties.get("loc")
            if loc and loc in loc_map:
                priority, file_stem = loc_map[loc]
                feature.properties["priority"] = priority
                feature.properties["img"] = file_stem

    def match_categories(self, categories: Dict[str, str] = {}):
        print("Matching business categories ...")
        for business in self.features.values():
            business.match_category(categories)

    def match_towns(self, census_places: Dict[str, Any]):
        print("Matching towns ...")
        for business in self.features.values():
            business.match_town(census_places)

    def geocode(self):
        print("Geocoding businesses:")
        for business in self.features.values():
            print(f"  {business.properties.get('id')}")
            business.geocode(self.name)

    def load_geojson(self, filename: str, keep_name = False):
        super().load_geojson(filename, obj_type=Business, keep_name=keep_name)