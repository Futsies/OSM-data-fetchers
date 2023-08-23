import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

def convert_incline_to_float(incline_str):
    """Converts an incline string to its float representation."""
    if incline_str == "up":
        return 0.1
    elif incline_str == "down":
        return -0.1
    elif incline_str.endswith("%"):
        return float(incline_str.strip("%")) / 100
    else:
        try:
            return float(incline_str)
        except ValueError:
            return 0.0

overpass_url = "http://overpass-api.de/api/interpreter"

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

overpass_query = ("""
[out:json];
(
  way["highway"="footway"](poly:"{polygon}");
);
out body;
>;
out skel qt;
""".format(polygon=" ".join(flat_coords)))

response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

features = []

# Create a dictionary mapping node ids to their coordinates
node_coords = {node['id']: (node['lon'], node['lat']) for node in data['elements'] if node['type'] == 'node'}

for element in data['elements']:
    if element['type'] == 'way':
        nodes = element['nodes']
        # Use the dictionary to look up coordinates for each node
        coords = [node_coords[i] for i in nodes]
        line = LineString(coords)
        feature = {
            'type': 'Feature',
            'properties': {
                'id': str(element['id']),
                'highway': element['tags'].get('highway', None),
                'footway': element['tags'].get('footway', None),
                'surface': element['tags'].get('surface', None),
                'width': float(element['tags'].get('width', 3)),
                'incline': convert_incline_to_float(element['tags'].get('incline', "0.1")),
                'smoothness': element['tags'].get('smoothness', 'unknown'),
                'crossing': element['tags'].get('crossing', 'unknown'),
                'curb': element['tags'].get('curb', 'unknown'),
                'sloped_curb': element['tags'].get('sloped_curb', 'unknown'),
                'tactile_paving': element['tags'].get('tactile_paving', 'unknown'),
                'description': element['tags'].get('description', 'no description'),
            },
            'geometry': line
        }
        features.append(feature)

gdf = gpd.GeoDataFrame(pd.DataFrame(features), geometry='geometry')
gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)
gdf.to_file("sidewalks.geojson", driver="GeoJSON")
