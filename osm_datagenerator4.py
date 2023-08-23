import overpy
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

api = overpy.Overpass()

# Given coordinates
coords = [
            [
              19.922511280259556,
              39.631094132250155
            ],
            [
              19.91475189690283,
              39.63405563756879
            ],
            [
              19.899027128863622,
              39.6339498717046
            ],
            [
              19.896967115582186,
              39.623954267870204
            ],
            [
              19.903421823861663,
              39.609249115382624
            ],
            [
              19.9292406569742,
              39.608191070283766
            ],
            [
              19.93528336259689,
              39.6235840325883
            ],
            [
              19.922511280259556,
              39.631094132250155
            ]
          ]


# Convert the list of coordinates to a flat list in "latitude longitude" format
flat_coords = [str(coord) for point in reversed(coords) for coord in reversed(point)]

# Construct the Overpass query
query = """
    [out:json][timeout:600];
    (
        way(poly:"{polygon}");
    );
    out body;
    >;
    out skel qt;
""".format(polygon=" ".join(flat_coords))

# Execute the query
result = api.query(query)

# Execute the query
result = api.query(query)

# Check if we have any data
if len(result.ways) == 0:
    print("No data fetched from the Overpass API for the specified polygon.")
    exit()

# Prepare a list to hold our ways
ways = []

# Each "way" in the result represents a feature
for way in result.ways:
    # The nodes of the way define its geometry
    line = LineString([(float(node.lon), float(node.lat)) for node in way.nodes])
    # We'll use the way's ID and tags as properties
    ways.append({
        'type': 'Feature',
        'id': way.id,
        'properties': way.tags,
        'geometry': line
    })

# Convert the ways to a list of GeoDataFrames
geodataframes = [gpd.GeoDataFrame.from_features([way], crs='EPSG:4326') for way in ways]

# Concatenate all the GeoDataFrames into one
gdf = gpd.GeoDataFrame(pd.concat(geodataframes, ignore_index=True), crs='EPSG:4326')

# Save the GeoDataFrame as a GeoJSON file
gdf.to_file("osm_data.geojson", driver='GeoJSON')
