from osgeo import ogr, gdal, osr
import zipfile
import os
import tempfile
import shutil
from datetime import datetime, timedelta


class Geom:
    tif_exts = (".tif", ".tiff", ".TIF", ".TIFF")
    @staticmethod
    def get_bounding_box_from_raster(raster_path: str) -> tuple[float, float, float, float]:
        """Retrieve the bounding box from a raster file."""
        dataset = gdal.Open(raster_path)
        if not dataset:
            raise ValueError(f"Could not open raster file: {raster_path}")
        geo_transform = dataset.GetGeoTransform()
        if not geo_transform:
            raise ValueError(f"Could not retrieve geotransform from raster file: {raster_path}")
        min_x = geo_transform[0]
        max_y = geo_transform[3]
        max_x = min_x + geo_transform[1] * dataset.RasterXSize
        min_y = max_y + geo_transform[5] * dataset.RasterYSize
        return min_x, min_y, max_x, max_y

    @staticmethod
    def get_bounding_box_from_vector(vector_path: str) -> tuple[float, float, float, float]:
        """Retrieve the bounding box from a vector file."""
        data_source = ogr.Open(vector_path)
        if not data_source:
            raise ValueError(f"Could not open vector file: {vector_path}")
        layer = data_source.GetLayer()
        extent = layer.GetExtent()
        return extent[0], extent[2], extent[1], extent[3]

    @staticmethod
    def get_bounding_box_from_safe_zip(zip_path: str) -> tuple[float, float, float, float]:
        """Retrieve the bounding box from a Sentinel-2 SAFE.zip file."""
        extracted_path = tempfile.mkdtemp()

        try:
            # Step 1: Extract the SAFE.zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_path)

            # Step 2: Find the granule image file to get the bounding box
            granule_path = None
            for root, dirs, files in os.walk(extracted_path):
                for file in files:
                    if file.endswith(".jp2") and "B01" in file:  # Assuming we use band B01 for the bounding box
                        granule_path = os.path.join(root, file)
                        break

            if granule_path is None:
                raise ValueError("Could not find the granule image file to extract bounding box.")

            # Step 3: Use GDAL to get the bounding box and determine the EPSG code
            dataset = gdal.Open(granule_path, gdal.GA_ReadOnly)
            if not dataset:
                raise ValueError(f"Could not open granule file: {granule_path}")

            try:
                geo_transform = dataset.GetGeoTransform()
                min_x = geo_transform[0]
                max_y = geo_transform[3]
                max_x = min_x + geo_transform[1] * dataset.RasterXSize
                min_y = max_y + geo_transform[5] * dataset.RasterYSize
                bounding_box = (min_x, min_y, max_x, max_y)

                # Attempt to determine the EPSG code from the dataset
                projection = dataset.GetProjection()
                source_sr = osr.SpatialReference()
                source_sr.ImportFromWkt(projection)
                if source_sr.IsProjected():
                    source_epsg = int(source_sr.GetAttrValue("AUTHORITY", 1))
                else:
                    raise ValueError("Could not determine the EPSG code from the granule file.")

                # Transform bounding box to WGS84
                bbox = Geom.transform_bounding_box_to_wgs84(bounding_box, source_epsg)
                bbox_adjusted = bbox[1], bbox[0], bbox[-1], bbox[-2]
                return bbox_adjusted
            finally:
                # Close the dataset to release the file
                dataset = None
        finally:
            # Clean up the extracted files
            shutil.rmtree(extracted_path)

    @staticmethod
    def transform_bounding_box_to_wgs84(bounding_box: tuple[float, float, float, float], source_epsg: int) -> tuple[float, float, float, float]:
        """Transform the bounding box coordinates to WGS84."""
        source_sr = osr.SpatialReference()
        source_sr.ImportFromEPSG(source_epsg)
        target_sr = osr.SpatialReference()
        target_sr.ImportFromEPSG(4326)  # WGS84

        transform = osr.CoordinateTransformation(source_sr, target_sr)

        min_x, min_y = transform.TransformPoint(bounding_box[0], bounding_box[1])[:2]
        max_x, max_y = transform.TransformPoint(bounding_box[2], bounding_box[3])[:2]

        return min_x, min_y, max_x, max_y

    @staticmethod
    def get_datetime_range_from_filename(filename: str) -> str:
        """Get a datetime range from the filename, with -1 hour to +1 hour of the timestamp in the name."""
        try:
            # Extract the timestamp from the filename
            parts = filename.split('_')
            timestamp_str = parts[2]
            timestamp = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%S")

            # Calculate the datetime range (-1 hour to +1 hour)
            start_time = timestamp - timedelta(hours=1)
            end_time = timestamp + timedelta(hours=1)

            # Format the datetime range as a string
            datetime_range = f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            return datetime_range
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid filename format: {filename}") from e

    @classmethod
    def merge_tifs(cls, input_dir, output_path):
        # Collect all file paths in the directory ending with .tif
        tif_files = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith(cls.tif_exts)]

        # Open each file and get the first band from each
        bands = [gdal.Open(tif) for tif in tif_files]

        # Get metadata from the first file for projection and geotransform
        cols = bands[0].RasterXSize
        rows = bands[0].RasterYSize
        geotransform = bands[0].GetGeoTransform()
        projection = bands[0].GetProjection()

        # Create a new multi-band GeoTIFF file
        driver = gdal.GetDriverByName('GTiff')
        out_raster = driver.Create(output_path, cols, rows, len(bands), gdal.GDT_Float32)

        # Set the geotransform and projection
        out_raster.SetGeoTransform(geotransform)
        out_raster.SetProjection(projection)

        # Write each band to the output file
        for index, band in enumerate(bands):
            out_band = out_raster.GetRasterBand(index + 1)
            out_band.WriteArray(band.ReadAsArray())
            out_band.FlushCache()

        print(f"Merged TIF saved at {output_path}")
