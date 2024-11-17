import os

from satlevel.ocean_plot.ocean_plot import OceanPlot


file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output', '25149.gpkg')


OceanPlot().plot_xy(file_path=file, x_col="observed", y_col="value", parameter_id="sealev_dvr")
