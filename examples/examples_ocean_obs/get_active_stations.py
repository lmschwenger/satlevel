import os

from satlevel.geom.geom import Geom
from satlevel.ocean_obs.ocean_obs import OceanObs


file_in = file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'test_aoi_2.shp')
filename, ext = os.path.splitext(os.path.basename(file_in))
file_out = os.path.join(os.path.dirname(__file__), '..', 'data', 'output', f"{filename}_active_stations{ext}")

bbox = Geom.get_bounding_box_from_vector(vector_path=file_in)

active_stations = OceanObs().get_active_stations_for_bbox(bbox=bbox)
print(f"{active_stations = }")
