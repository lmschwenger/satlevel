import os

from satlevel.ocean_plot.ocean_plot import OceanPlot

file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output',
                    'water_level_S2B_MSIL2A_20240921T104629_N0511_R051_T32UMG_20240921T135519')


OceanPlot().plot_all_stations(directory_path=file, x_col="observed", y_col="value", parameter_id="sea_reg")
