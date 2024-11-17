from satlevel.geom.geom import Geom
import os


file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'test_aoi_1.shp')

bbox = Geom.get_bounding_box_from_vector(vector_path=file)

print(f"{bbox = }")
