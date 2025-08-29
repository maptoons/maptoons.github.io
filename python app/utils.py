import html
import json
import os
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

WINDOWS_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3"
STREET_TYPES = [" Ave", " Rd", " St", " Pl", " Blvd", " Dr", " Pkwy", " Ln"]


def load_json(filename: str) -> Any:
    with open(filename, "r") as f:
        json_data = json.load(f)
    return json_data


def make_geojson(name: str, features: dict, output_filename: str):
    geojson = {
        "type": "FeatureCollection",
        "name": name,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }
    with open(output_filename, "w") as f:
        json.dump(geojson, f, indent=4, ensure_ascii=False)


def scrape(url: str, user_agent: str = WINDOWS_CHROME) -> Any:
    headers = {"User-Agent": user_agent}
    r = requests.get(url, headers)
    r.raise_for_status()
    return r.content


def scrape_html(url: str, root_tag: list[str], user_agent: str = WINDOWS_CHROME) -> BeautifulSoup:
    html_content = scrape(url, user_agent)
    return BeautifulSoup(html_content, features="html.parser").find(*root_tag)


# TODO: When the geocoder is confused, it returns multiple matches
def geocode(address: str, api_key_env: str = "GEOAPIFY_API_KEY"):
    api_key = os.getenv(api_key_env)
    address = html.escape(address.strip())
    headers = {"Accept": "application/json"}
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
    r = requests.get(url, headers)
    r.raise_for_status()
    r_json = r.json()
    features = r_json.get("features")
    if features:
        f = features[0]
        props = f.get("properties", None)
        geo = f.get("geometry", None)
        formatted = props.get("formatted", "")
        return formatted, geo
    return "", None


def bounding_box(geometry: Dict[str,Any]) -> Dict[str,Any]:
    geo_type = geometry.get("type")
    if geo_type not in ["MultiPolygon"]:
        raise NotImplementedError(geo_type)

    min_pt, max_pt = [], []

    polygons = geometry.get("coordinates", [])
    for poly in polygons:
        outer = poly[0]
        for pt in outer:
            if not min_pt:
                min_pt = pt
                max_pt = pt
                continue

            lon, lat = pt
            min_lon, min_lat = min_pt
            max_lon, max_lat = max_pt
            min_pt = [min(lon, min_lon), min(lat, min_lat)]
            max_pt = [max(lon, max_lon), max(lat, max_lat)]
    
    return {
        "type": "MultiPoint",
        "coordinates": [min_pt, max_pt],
    }

def address_suffix(address: str, street_types: List[str] = STREET_TYPES):
    addr = address.replace(".", "")
    for st in street_types:
        if st in addr:
            return address.split(st)[-1]
    return ""

def ascii_only(s: str, alphabet="abcdefghijklmnopqrstuvwxyz", space="_") -> str:
    s_out = ""
    for c in s.lower().strip().replace(" ", space):
        if c in alphabet:
            s_out += c
    return s_out
