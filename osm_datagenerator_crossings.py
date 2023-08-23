import overpy
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


# Fetch all ways in Corfu that are footways or have a crossing tag
result = api.query("""
    [out:json];
    (
      way["highway"="footway"](poly:"{polygon}");
      way["crossing"](poly:"{polygon}");
    );
    out body;
    >;
    out skel qt;
""".format(polygon=" ".join(flat_coords)))

# Prepare a list to hold our ways
ways = []

# Define a list of tags that we're interested in
tags_of_interest = ['surface', 'highway', 'crossing']  # Add any other tags that you're interested in

# Each "way" in the result represents a feature
for way in result.ways:
    # The nodes of the way define its geometry
    line = LineString([(float(node.lon), float(node.lat)) for node in way.nodes])

    # Filter the way's tags to include only those we're interested in
    properties = {k: v for k, v in way.tags.items() if k in tags_of_interest}

    # Only add the way to the list of features if it doesn't have a "crossing" tag with a 'null' value
    if ('crossing' in properties and properties['crossing'] != 'null'):
        # We'll use the way's ID and filtered tags as properties
        ways.append({'type': 'Feature',
                     'id': way.id,
                     'properties': properties,
                     'geometry': line})

# Only attempt to create the GeoDataFrame if there are ways in the result
if ways:
    # Convert the ways to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(ways, crs='EPSG:4326')

    # Save the GeoDataFrame as a GeoJSON file
    gdf.to_file("crossings.geojson", driver='GeoJSON')
else:
    print("No ways found in the specified area.")
