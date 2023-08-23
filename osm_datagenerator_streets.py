import overpy
import geopandas as gpd
from shapely.geometry import LineString

api = overpy.Overpass()

# Fetch all ways in Corfu that are footways or have a crossing tag
result = api.query("""
    [out:json];
    (
      way["highway"="footway"](39.600938,19.868314,39.629214,19.934180);
      way["sidewalk"](39.600938,19.868314,39.629214,19.934180);
    );
    out body;
    >;
    out skel qt;
""")

# Prepare a list to hold our ways
ways = []

# Define a list of tags that we're interested in
tags_of_interest = ['surface', 'highway', 'sidewalk']  # Add any other tags that you're interested in

# Each "way" in the result represents a feature
for way in result.ways:
    # The nodes of the way define its geometry
    line = LineString([(float(node.lon), float(node.lat)) for node in way.nodes])

    # Filter the way's tags to include only those we're interested in
    properties = {k: v for k, v in way.tags.items() if k in tags_of_interest}

    # Only add the way to the list of features if the highway key is a "footway"
    if ('highway' in properties and (properties['highway'] != 'footway') or ()):
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
    gdf.to_file("sidewalks.geojson", driver='GeoJSON')
else:
    print("No ways found in the specified area.")
