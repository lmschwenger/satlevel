from satlevel.geom.geom import Geom
import os

from satlevel.ocean_obs.ocean_obs import OceanObs

file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'test_aoi_2.shp')

bbox = Geom.get_bounding_box_from_vector(vector_path=file)



print(f"{bbox = }")

OceanObs().retrieve_stations_data(bbox=bbox, output_directory=os.path.join(os.path.dirname(file), 'output'),
                                  datetime_range="2018-02-12T00:00:00Z/2018-03-18T00:00:00Z")
