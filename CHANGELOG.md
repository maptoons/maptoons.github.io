# Changelog

## 2026-08-06 Release

### Added
- Data ponts for Island Park, NY. Images for points are in `img` directory with prefixes 'IP'. GeoJSON formatted data is found in the data directory in `island_park.geojson`.

### Changed
- Priority values for Premium Advertisers in Baldwin and Island Park. Changes made in `data/baldwin.geojson` and `data/island_park.geojson`.

## 2026-08-05 Release

### Added
- Filtering logic to `water_polygons_labels` in `maptoons.json` to prevent labels for 'basins' from rendering. This addition is to reduce visual clutter in the map area.
- Filtering logic to `water_polygons_labels` in `maptoons.json` to only render labels for water with property `way_area` exceeding 2000 square meters. This currently does not filter many water bodies out, but was left in place for ease of future adjustment if needed.
- Data points for Baldwin, NY. Images for points are in `img` directory with prefixes 'BW'. GeoJSON formatted data is found in the data directory in `baldwin.geojson`.
- Navigation links to map areas for Baldwin, NY and Island Park, NY with map animation logic in the 'city finder' drop down menu.

Changes authored by Simon - simon@simonconrad.com

## 2026-03-16 Release

### Enhancements
- **Basemap Updates**: Added OpenStreetMap (OSM) railroad data to the basemap utilizing shortbread vector tiles, including documentation on data sourcing and styling adjustments.
- **Waterway Layers**: Integrated missing waterway layers and labels on the map using OSM data and shortbread vector tiles for enhanced detail.
- **Railway Station Rendering**: Implemented custom design for rendering railway stations in the Long Island Railroad and New Jersey Transit systems, aligned with actual railroad sign styles using custom sprites. **Note:** To manage the distinct rendering of these train stations, GeoJSON data for the stations is included as static assets in the code repository rather than fetched dynamically from OSM. This data is found in `/data/railroad/` directory.

### Design Improvements
- **Railroad Line Pattern**: Developed a custom design for the railroad line pattern to improve the interactive web map's aesthetic, aligning it more closely with the MapToons print map design.
- **Waterway Style Cleanup**: Conducted a cleanup of existing styles for waterways, enhancing labeling and zoom-dependent styling for better legibility.

### Dynamic Features
- **Dynamic Styling for Railroads**: Added dynamic styling properties to the railroad layer, allowing three levels of design detail based on the user's zoom level.

### Performance Updates
- **Map Rendering Optimization**: Updated the MapLibre pixel ratio configuration to improve rendering quality, ensuring crisp visuals on retina and retina-like mobile displays, addressing pixelation and text legibility issues.
