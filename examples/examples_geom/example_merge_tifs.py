import os

from satlevel.geom.geom import Geom


folder = "20230904"
#input_dir = os.path.join(r"C:\rs_dev\change_detection\case_1_wadden\imgs", folder)
input_dir = os.path.join(r"C:\rs_dev\change_detection\case_2_laesoe\imgs", folder)
output_path = os.path.join(input_dir, f"{folder}.tif")
Geom().merge_tifs(input_dir=input_dir, output_path=output_path)