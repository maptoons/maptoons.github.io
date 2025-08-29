import re
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from utils import geocode, bounding_box, address_suffix, ascii_only


class Feature:
    def __init__(self, properties: Dict[str, Any] = None, geometry: Dict[str, Any] = None):
        self.properties = properties if properties is not None else None
        self.geometry = geometry if geometry is not None else None

    def update(self, properties: Dict[str, Any] = None, geometry: Dict[str, Any] = None):
        if properties:
            if self.properties:
                self.properties.update(properties)
            else:
                self.properties = properties
        if geometry:
            if self.geometry:
                self.geometry.update(geometry)
            else:
                self.geometry = geometry

    @property
    def feature(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "properties": self.properties,
            "geometry": self.geometry,
        }


class Location(Feature):
    def __init__(self, properties: Dict[str, Any] = None, geometry: Dict[str, Any] = None):
        super().__init__(properties, geometry)

    def load_html(self, node: BeautifulSoup, data_folder: str = "data"):
        url = node.div.a["href"]
        filename = url.split(".")[0]

        year_match = re.match(r"\d{4}", filename.split("-")[-1])

        filename = "-".join(filename.split("-")[:-1]) if year_match else filename
        interactive = "interactive map" in [s.lower() for s in node.stripped_strings]

        self.properties = {
            "name": filename.replace("-", " ").title(),
            "data": f"{data_folder}/{filename}.geojson",
            "source": url,
            "interactive": interactive,
            "year": int(year_match.group()) if year_match else 0,
        }

    def _find_matching_geometry(self, geojson: Dict[str, Any]):
        for feature in geojson["features"]:
            if self.properties.get("name") in feature["properties"]["NAME"]:
                return feature["geometry"]
        return None
    
    def bounding_box(self, geojson: Dict[str, Any]):
        match = self._find_matching_geometry(geojson)
        if match:
            self.geometry = bounding_box(match)

    def match_geometry(self, geojson: Dict[str, Any]):
        match = self._find_matching_geometry(geojson)
        if match:
            self.geometry = match


class Business(Feature):
    def _clean_strs(list_strs: List[str]):
        text = " ".join(list_strs)
        text = text.split(":")[-1]
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    def _extract_tag_data(tag: BeautifulSoup) -> Tuple[str, str]:
        attribute = tag["class"][0].lower()
        data = None
        if attribute in ["web", "email"]:
            tag = tag.find("a")
            if tag and "href" in tag.attrs and tag["href"] != "#":
                data = tag["href"].replace("mailto:", "")
            if data and data.find("facebook.com") >= 0:
                attribute = "facebook"
            elif data and data.find("instagram.com") >= 0:
                attribute = "instagram"
        else:
            if attribute in ["category"]:
                attribute = "business"
            data = Business._clean_strs(tag.stripped_strings)
        return attribute, data

    def _extract_website(website: str) -> Dict[str, str]:
        if website.find("IG @") >= 0:
            handle = website.replace("IG @", "").strip()
            return {"instagram": f"https://www.instagram.com/{handle}/"}
        elif website.find("FB @") >= 0:
            handle = website.replace("FB @", "").strip()
            return {"facebook": f"https://www.facebook.com/{handle}"}
        elif website.find("http") == -1:
            return {"web": f"http://{website}"}
        return website

    def _clean_favico_url(index_url: str, img_url: str) -> str:
        parsed_index_url = urlparse(index_url)
        parsed_img_url = urlparse(img_url)

        if img_url in ["data:;"]:
            return ""

        if not parsed_img_url.scheme and parsed_img_url.netloc:
            return f"{parsed_index_url.scheme}:{img_url}"

        if not parsed_img_url.scheme and not parsed_img_url.netloc:
            path = parsed_img_url.path
            if path[0] != "/":
                path = "/" + path
            return f"{parsed_index_url.scheme}://{parsed_index_url.netloc}{path}"

        return img_url

    def __init__(self, properties: Dict[str, Any] = None, geometry: Dict[str, Any] = None):
        super().__init__(properties, geometry)

    def load_html(self, node: BeautifulSoup, target_tags=[["p"],["h3"]]):
        properties = {"id": node["id"]}
        for target_tag in target_tags:
            for tag in node.find_all(*target_tag):
                if "class" not in tag.attrs:
                    continue

                attrib, data = Business._extract_tag_data(tag)
                if attrib and data:
                    properties.update({attrib: data})

            self.update(properties)

    def load_csv(self, row: Dict[str, Any]):
        properties = {
            "id": ascii_only(row["Business"], space=""),
            "address": row["Address"],
            "town": row["Town"],
            "business": row["Category"],
            "info": row["DL Info"],
            "mapname": row["Business"],
            "loc": int(re.search(r"\d+", row["LOC"]).group())
        }
        if row["Phone"]:
            properties.update({"phone": row["Phone"]})
        if row["Shoppers Discount"]:
            properties.update({"discount": row["Shoppers Discount"]})
        if row["Exp."]:
            properties.update({"exp": row["Exp."]})
        if row["Website"]:
            properties.update(Business._extract_website(row["Website"]))
        self.update(properties)

    def match_category(self, category_json: Dict[str, Any], default_category=""):
        self.properties["category"] = default_category
        self.properties["subcategory"] = default_category
        for k, v in category_json.items():
            category = v.get("category")
            subcategory = v.get("subcategory")
            if "business" in self.properties and self.properties["business"] == k:
                self.properties["category"] = category
                self.properties["subcategory"] = subcategory
                break

    def match_town(self, geojson: Dict[str, Any]):
        if "town" not in self.properties and "address" in self.properties:
            for feature in geojson["features"]:
                town = feature["properties"]["NAME"]
                if town in address_suffix(self.properties["address"]):
                    self.properties["town"] = town

    def geocode(self, default_context=""):
        town, state = default_context.split(",")
        if "town" in self.properties:
            town = self.properties["town"]
        if "address" in self.properties:
            address: str = self.properties["address"]
            address = address.replace("#", "No.").replace("&", "and").replace("'", "")
            address_formatted, geometry = geocode(f"{address} {town} {state}")
            self.properties["address_formatted"] = address_formatted
            self.geometry = geometry
