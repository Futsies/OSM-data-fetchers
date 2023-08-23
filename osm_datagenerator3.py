import overpy
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

api = overpy.Overpass()

# Fetch all ways in Corfu
result = api.query("""
    [out:json];
    (way({south},{west},{north},{east}););
    out body;
    >;
    out skel qt;
""".format(north=39.675, south=39.624, west=19.849, east=19.922))

# Prepare a list to hold our ways
ways = []

# Each "way" in the result represents a feature
for way in result.ways:
    # The nodes of the way define its geometry
    line = LineString([(float(node.lon), float(node.lat)) for node in way.nodes])
    # We'll use the way's ID and tags as properties
    ways.append({'type': 'Feature',
                 'id': way.id,
                 'properties': way.tags,
                 'geometry': line})

# Convert the ways to a GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(ways, crs='EPSG:4326')

# Save the GeoDataFrame as a GeoJSON file
gdf.to_file("osm_data.geojson", driver='GeoJSON')
