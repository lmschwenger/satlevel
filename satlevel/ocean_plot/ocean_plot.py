import os
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from osgeo import ogr


class OceanPlot:
    def plot_xy(self, file_path: str, x_col: str, y_col: str, parameter_id: str | None = None) -> None:
        """Plot data from a GeoPackage file using specified x and y columns."""
        data_source = ogr.Open(file_path)
        if not data_source:
            raise ValueError(f"Could not open file: {file_path}")
        layer = data_source.GetLayer()
        x_values = []
        y_values = []
        for feature in layer:
            val_parameter_id = feature.GetField("parameterId")
            if val_parameter_id == "tw":
                continue
            if parameter_id and val_parameter_id != parameter_id:
                continue
            x = feature.GetField(x_col)
            y = feature.GetField(y_col)
            if x is not None and y is not None:
                try:
                    x = datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    continue
                x_values.append(x)
                y_values.append(y)
        fig, ax = plt.subplots()
        ax.scatter(x_values, y_values, label="Filtered Data", color='b')
        ax.set_xlabel(x_col)

        if parameter_id:
            ax.set_ylabel(parameter_id)
        else:
            ax.set_ylabel(y_col)
        ax.set_title(f"Scatter Plot of {y_col} vs {x_col}")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_all_stations(self, directory_path: str, x_col: str, y_col: str, parameter_id: str | None = None) -> None:
        """Plot data from multiple GeoPackage files in a specified directory."""
        station_data = {}

        # Iterate through all files in the directory
        for file_name in os.listdir(directory_path):
            if file_name.endswith(".gpkg"):
                file_path = os.path.join(directory_path, file_name)
                data_source = ogr.Open(file_path)
                if not data_source:
                    raise ValueError(f"Could not open file: {file_path}")
                layer = data_source.GetLayer()
                station_name = os.path.splitext(file_name)[0]
                x_values = []
                y_values = []
                for feature in layer:
                    val_parameter_id = feature.GetField("parameterId")
                    if val_parameter_id == "tw":
                        continue
                    if parameter_id and val_parameter_id != parameter_id:
                        continue
                    x = feature.GetField(x_col)
                    y = feature.GetField(y_col)
                    if x is not None and y is not None:
                        try:
                            x = datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            continue
                        x_values.append(x)
                        y_values.append(y)
                if x_values and y_values:
                    station_data[station_name] = (x_values, y_values)

        # Create the plot
        fig, ax = plt.subplots()
        colors = plt.cm.get_cmap('tab10', len(station_data))

        for idx, (station_name, (x_vals, y_vals)) in enumerate(station_data.items()):
            ax.scatter(x_vals, y_vals, label=station_name, color=colors(idx))

        ax.set_xlabel(x_col)
        if parameter_id:
            ax.set_ylabel(parameter_id)
        else:
            ax.set_ylabel(y_col)
        ax.set_title(f"Scatter Plot of {y_col} vs {x_col} for All Stations")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()