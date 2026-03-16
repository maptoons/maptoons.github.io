# Changelog

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
