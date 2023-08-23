import fiona
import os
import warnings
from fiona import FionaDeprecationWarning

# Suppress warnings
warnings.filterwarnings("ignore", category=FionaDeprecationWarning)

sidewalks_input_file = "../../opensidewalks-data/data_fetchers/sidewalks.geojson"
crossings_input_file = "../../opensidewalks-data/data_fetchers/crossings.geojson"
output_file = "transportation.geojson"
new_id = 0

def process_features(source, features, footway_type):
    #new_id = 0

    for feature in source:
        # Check if the 'properties' field exists within the outer 'properties' field
        if 'properties' in feature['properties']:
            nested_properties = feature['properties']['properties']
        else:
            nested_properties = feature['properties']

        new_feature = {
            'type': 'Feature',
            'properties': {
                'footway': footway_type,
                'marked': nested_properties.get('marked', 'null'),
		'subclass': nested_properties.get('subclass', 'footway'),
		'surface': nested_properties.get('surface', 'null'),
                'width': nested_properties.get('width', 3),
		'length': nested_properties.get('length', 4),
                'incline': nested_properties.get('incline', "0.05"),
                'layer': nested_properties.get('layer', 'null'),
		#'smoothness': nested_properties.get('smoothness', "unknown"),
                #'crossing': nested_properties.get('crossing', "unknown"),
                'curbramps': nested_properties.get('curbramps', "unknown"),
                #'sloped_curb': nested_properties.get('sloped_curb', "unknown"),
                #'tactile_paving': nested_properties.get('tactile_paving', "unknown"),
                'description': nested_properties.get('description', "no description"),
                #'fid': str(new_id) #"way/" + str(new_id),
		'id': nested_properties.get('id'), #, str(new_id)), #"way/" + str(new_id),
            },
            'geometry': feature['geometry'],
        }
        globals()["new_id"] += 1 #new_id += 1

        features.append(new_feature)



def create_schema():
    return {
        'geometry': 'LineString',  # adjust this to your needs
        'properties': {
            'footway': 'str',
            'marked': 'float',
	    'subclass': 'str',
	    'surface': 'str',
            'width': 'float',
	    'length': 'float',
	    'layer': 'str',
            'incline': 'str',
            #'smoothness': 'str',
            #'crossing': 'str',
            'curbramps': 'str',
            #'sloped_curb': 'str',
            #'tactile_paving': 'str',
            'description': 'str',
            'id': 'str',
        }
    }

# Open the source GeoJSON files
with fiona.open(sidewalks_input_file, 'r') as source:
    features = []
    process_features(source, features, 'sidewalk')
    input_crs = source.crs

with fiona.open(crossings_input_file, 'r') as source:
    process_features(source, features, 'crossing')

# Create a new schema
output_schema = create_schema()

# Write the new GeoJSON file
with fiona.open(output_file, 'w', crs=input_crs, driver="GeoJSON", schema=output_schema) as sink:
    sink.writerecords(features)
