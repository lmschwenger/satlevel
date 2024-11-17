from osgeo import ogr


class Geom:
    def __init__(self, file_path):
        self.file_path = file_path
        self.bounding_box = self.get_bounding_box()

    def get_bounding_box(self):
        # Open the file using GDAL
        data_source = ogr.Open(self.file_path)
        if not data_source:
            raise ValueError(f"Could not open file: {self.file_path}")

        # Get the layer from the data source
        layer = data_source.GetLayer()
        # Get the extent of the layer, which returns (minX, maxX, minY, maxY)
        extent = layer.GetExtent()
        # Bounding box with two sets of (X, Y) coordinates: (minX, minY), (maxX, maxY)
        bounding_box = extent[0], extent[2], extent[1], extent[3]

        return bounding_box
