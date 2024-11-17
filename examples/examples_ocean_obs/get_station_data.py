from satlevel.geom.geom import Geom
import os

from satlevel.ocean_obs.ocean_obs import OceanObs

file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'test_aoi_2.shp')

geom = Geom(file_path=file)

bbox = geom.get_bounding_box()

print(f"{bbox = }")

OceanObs().save_observations_to_station_files(bbox=bbox, output_directory=os.path.join(os.path.dirname(file), 'output'),
                                              datetime_range="2018-02-12T00:00:00Z/2018-03-18T00:00:00Z")
