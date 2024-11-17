from satlevel.geom.geom import Geom
import os

from satlevel.ocean_obs.ocean_obs import OceanObs

file = os.path.join(os.path.dirname(__file__), '..', 'data',
                    'S2B_MSIL2A_20240921T104629_N0511_R051_T32UMG_20240921T135519.SAFE.zip')
foldername = os.path.splitext(os.path.splitext(f"water_level_{os.path.basename(file)}")[0])[0]
output_dir = os.path.join(os.path.dirname(file), 'output', foldername)

bbox = Geom.get_bounding_box_from_safe_zip(zip_path=file)
print(f"{bbox = }")

datetime_range = Geom.get_datetime_range_from_filename(filename=os.path.basename(file))
print(f"{datetime_range = }")

OceanObs().retrieve_stations_data(bbox=bbox, datetime_range=datetime_range, output_directory=output_dir)

