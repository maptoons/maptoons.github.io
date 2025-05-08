## mbtiles to mvt

# long island
tippecanoe -o long_island.mbtiles long_island.geojson \
  --no-tile-compression \
  --minimum-zoom=7 \
  --maximum-zoom=18 \
  --drop-densest-as-needed \
  --force
# convert
rm -rf long_island
ogr2ogr -f MVT long_island long_island.mbtiles -dsco MINZOOM=7 -dsco MAXZOOM=18 -dsco COMPRESS=NO

# highways
tippecanoe -o long_island_highway.mbtiles long_island_highway.geojson \
  --no-tile-compression \
  --minimum-zoom=11 \
  --maximum-zoom=18 \
  --drop-densest-as-needed \
  --low-detail=5 \
  --full-detail=9 \
  --force
# convert
rm -rf long_island_highway
ogr2ogr -f MVT long_island_highway long_island_highway.mbtiles -dsco MINZOOM=11 -dsco MAXZOOM=18 -dsco COMPRESS=NO

# places
tippecanoe -o long_island_place.mbtiles long_island_place.geojson \
  --no-tile-compression \
  --minimum-zoom=7 \
  --maximum-zoom=12 \
  --force
# convert
rm -rf long_island_place
ogr2ogr -f MVT long_island_place long_island_place.mbtiles -dsco MINZOOM=7 -dsco MAXZOOM=12 -dsco COMPRESS=NO

