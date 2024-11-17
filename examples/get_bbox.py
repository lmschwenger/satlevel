from satlevel.geom.geom import Geom
import os


file = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_aoi_1.shp')

geom = Geom(file_path=file)

bbox = geom.get_bounding_box()

print(f"{bbox = }")
