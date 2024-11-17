import os
import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal, osr

class ChangeAnalysis:
    @classmethod
    def load_image_stack(cls, images: list[str]):
        bands = []
        for band_file in images:
            dataset = gdal.Open(band_file)
            band_data = dataset.ReadAsArray()  # Read the band as a 2D numpy array
            bands.append(band_data)
        return np.stack(bands, axis=2)  # Stack bands along the third dimension

    @classmethod
    def get_image_paths_from_s2_dir(cls, s2_dir: str) -> list[str]:
        images = []
        for band in bands:
            for img in os.listdir(s2_dir):
                if band in img:
                    images.append(os.path.join(s2_dir, img))
        return images
    @classmethod
    def load_image_stack_from_s2_dir(cls, img_dir: str, bands: list[str]):
        images = cls.get_image_paths_from_s2_dir(img_dir)
        stack = cls.load_image_stack(images)
        return stack

    @classmethod
    def _compute_ndwi(cls, green_band, nir_band):
        # Calculate NDWI
        ndwi = (green_band - nir_band) / (green_band + nir_band)
        # Handle division by zero and NaN values
        ndwi = np.nan_to_num(ndwi, nan=-1)
        return ndwi

    @classmethod
    def _mask_land_areas(cls, stack, threshold=0):
        # Assume Green is band 1 (B03) and NIR is band 3 (B08) in the stack
        green_band = stack[:, :, 1]
        nir_band = stack[:, :, 3]

        # Calculate NDWI
        ndwi = cls._compute_ndwi(green_band, nir_band)

        # Create a water mask (1 for water, 0 for land)
        water_mask = (ndwi > threshold).astype(int)
        return water_mask

    @classmethod
    def _compute_change_magnitude(cls, stack_1, stack_2):
        change_vectors = stack_2 - stack_1
        return np.linalg.norm(change_vectors, axis=2)

    @classmethod
    def save_change_magnitude_as_geotiff(cls, change_magnitude, water_mask, reference_path, output_path):
        # Apply the water mask to set land areas as NoData
        change_magnitude[water_mask == 0] = np.nan  # Set land areas as NaN

        # Open the reference dataset to get geotransformation and projection
        reference_dataset = gdal.Open(reference_path)
        geotransform = reference_dataset.GetGeoTransform()
        projection = reference_dataset.GetProjection()

        # Create a new GeoTIFF file
        driver = gdal.GetDriverByName("GTiff")
        out_raster = driver.Create(output_path, reference_dataset.RasterXSize, reference_dataset.RasterYSize, 1, gdal.GDT_Float32)
        out_raster.SetGeoTransform(geotransform)
        out_raster.SetProjection(projection)

        # Write the change magnitude to the new file
        out_band = out_raster.GetRasterBand(1)
        out_band.WriteArray(change_magnitude)

        # Set NoData value
        out_band.SetNoDataValue(np.nan)

        # Flush and close the dataset
        out_band.FlushCache()
        out_raster = None
        print(f"Saved change magnitude to {output_path}")

    @classmethod
    def compute_temporal_change(cls, images_1, images_2, output_path):
        stack_1 = cls.load_image_stack(images_1)
        stack_2 = cls.load_image_stack(images_2)

        # Mask land areas
        water_mask = cls._mask_land_areas(stack_1)

        # Compute change magnitude
        change_magnitude = cls._compute_change_magnitude(stack_1, stack_2)

        # Save the change magnitude as a GeoTIFF
        cls.save_change_magnitude_as_geotiff(change_magnitude, water_mask, images_1[0], output_path)

# Directories and bands
dir_1 = r"C:\rs_dev\change_detection\case_2_laesoe\imgs\20200901"
dir_2 = r"C:\rs_dev\change_detection\case_2_laesoe\imgs\20230904"
bands = ["B02", "B03", "B04", "B08"]

images_1 = ChangeAnalysis.get_image_paths_from_s2_dir(s2_dir=dir_1)
images_2 = ChangeAnalysis.get_image_paths_from_s2_dir(s2_dir=dir_2)
# Output path for the change magnitude GeoTIFF
output_path = r"C:\rs_dev\change_detection\case_2_laesoe\change_magnitude.tif"

# Compute temporal change and save the result
ChangeAnalysis.compute_temporal_change(images_1, images_2, output_path)
