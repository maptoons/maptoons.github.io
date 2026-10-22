"""Convert a "latitude, longitude" pair (e.g. copied from Google Maps)
into a GeoJSON-style [longitude, latitude] coordinate array.

Usage:
    python latlon_to_lonlat.py "40.793463, -73.694879"
    python latlon_to_lonlat.py 40.793463 -73.694879
    python latlon_to_lonlat.py            # prompts for input
"""

import sys


def latlon_to_lonlat(text):
    parts = text.replace(',', ' ').split()
    if len(parts) != 2:
        raise ValueError(f'Expected "latitude, longitude", got: {text!r}')
    lat, lon = (float(p) for p in parts)
    if not -90 <= lat <= 90:
        raise ValueError(f'Latitude {lat} is out of range (-90 to 90). Is the input in "latitude, longitude" order?')
    if not -180 <= lon <= 180:
        raise ValueError(f'Longitude {lon} is out of range (-180 to 180).')
    return [lon, lat]


def main():
    text = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else input('latitude, longitude: ')
    try:
        lon, lat = latlon_to_lonlat(text)
    except ValueError as error:
        sys.exit(f'Error: {error}')
    print(f'[{lon}, {lat}]')


if __name__ == '__main__':
    main()
