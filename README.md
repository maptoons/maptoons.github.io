# maptoons-data

Written in python, this data pipeline takes a list of data files (.csv or .html) as input and produces an individual .geojson output data file for each input file.

## Overview
### Phase I

1. An input file is retrieved and parsed.

- If the input is an existing .html file hosted on maptoons.com, the file is requested from the web server and the html is parsed.

- Otherwise, if the input is a .csv spreadsheet, the file is read from disk and the spreadsheet is parsed. The header row of the spreadsheet defines the data structure.

2. As each business listing is being processed in the parsed file, various automated corrections and amendments are applied to the data. Some examples:

- If a business website points to instagram.com or facebook.com the corresponding data field will be `instagram` or `facebook` and not `website`.
- If a business `address` contains a town name, that name is extracted and assigned to the `town` attribute. This is helpful later in the geocoding step.
- The existing business description is used to assign a more general business category ('Eat & Drink', 'Learn and Play', etc.).

3. For those business listings that have a street `address`, the location of that business is assigned using a geocoder that takes the `address` and `town` as input. The geocoder produces a standardized `addressed_formatted` field and a `geometry` object that denotes the global position of the business in longitude and latitude.

4. Once all the listings are retrieved and geocoding has been attempted for each, the listings are saved to disk as a single .geojson file.

### Phase II

5. A .geojson file is retrieved and parsed. The .geojson contains all the business listings for a single maptoons map and geometry for each list as determined by the geocoder.

6. A second _corrections.geojson file is loaded that supplies supplementary or corrected data for a subset of businesses in the maptoons map. There can be several reasons for this. For example, the geocoder sometimes is inaccurate or not precise enough and slight adjustments to the longitude and latitude values are needed. The _corrections.geojson files serve to record all the manual adjustments made to the dataset *after* the primary data retrieval and geocoding steps.

7. If the initial data source was a .html file on the maptoons server, a .csv spreadsheet can be loaded at this point to assign a `LOC` identifier to each business listing.

8. If a folder of images containing business logos is available, these are assigned to corresponding business listings by referencing the `LOC` identifier specified in the listing and in the image file name. The `priority` of the business listing ('S', 'D', 'T', 'Q', 'P') is also set based on the image file name.

9. Once all the listings are corrected and logos have been assigned for each, the listings are again saved to disk as a single .geojson file.

## Geocoder

The geocoder converts a street address like `47 Elliot Drive, Hicksville, NY 11801` into a corresponding geometry like this:

```
"geometry": {
    "coordinates": [-73.5234, 40.75658],
    "type": "Point"
}
```

A number of different geocoding services exist on the internet and most require payment for each API call. This pipeline uses a service from geoapify.com. A unique API key can be attained from geoapify.com and stored in a special environment variable `GEOAPIFY_API_KEY` which is referenced by the pipeline.

## Editing .geojson Files

Like standard .json files, .geojson files are human readable and extremely flexible. They can be manually edited to add new properties to some or all of the features in the file. All modern programming languages can easily import, edit and export data saved in .json or .geojson files. Here, we use the json module from the python standard library to load and save .geojson files.

To visualize changes to feature geometry, it is best to use some form of graphical interface. The [maptoons admin page](https://maptoons.github.io/maptoons-admin.html) provides an easy way to load a .geojson, view and edit the feature geometries, and export the modified features as a new .geojson file.
