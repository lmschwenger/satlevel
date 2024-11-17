import os

from satlevel.geom.geom import Geom
from satlevel.ocean_obs.ocean_obs import OceanObs

file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_aoi_2.shp')

geom = Geom(file_path=file)

bbox = geom.get_bounding_box()
station_id = OceanObs().get_stationid(bbox=bbox)
print(f"{station_id = }")
