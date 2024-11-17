import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal


def load_bands(band_files):
    bands = []
    for band_file in band_files:
        dataset = gdal.Open(band_file)
        band_data = dataset.ReadAsArray()  # Read the band as a 2D numpy array
        bands.append(band_data)
    return np.stack(bands, axis=2)  # Stack bands along the third dimension


files_0 = [
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20200813\2020-08-13-00_00_2020-08-13-23_59_Sentinel-2_L2A_B02_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20200813\2020-08-13-00_00_2020-08-13-23_59_Sentinel-2_L2A_B03_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20200813\2020-08-13-00_00_2020-08-13-23_59_Sentinel-2_L2A_B04_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20200813\2020-08-13-00_00_2020-08-13-23_59_Sentinel-2_L2A_B08_(Raw).tiff"
]

files_1 = [
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20230417\2023-04-17-00_00_2023-04-17-23_59_Sentinel-2_L2A_B02_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20230417\2023-04-17-00_00_2023-04-17-23_59_Sentinel-2_L2A_B03_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20230417\2023-04-17-00_00_2023-04-17-23_59_Sentinel-2_L2A_B04_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20230417\2023-04-17-00_00_2023-04-17-23_59_Sentinel-2_L2A_B08_(Raw).tiff"
]
# Example usage
files_2 = [
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B02_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B03_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B04_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B08_(Raw).tiff"
]  # List of band files

image_stack_1 = load_bands(files_0)
image_stack_2 = load_bands(files_2)


# Calculate the difference in reflectance values for each band
change_vectors = image_stack_2 - image_stack_1

change_magnitude = np.linalg.norm(change_vectors, axis=2)

# Apply a threshold to detect significant changes
threshold = np.percentile(change_magnitude, 90)  # Example: Top 10% of changes
change_mask = (change_magnitude > threshold).astype(int)

plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(change_magnitude, cmap='hot')
plt.title('Change Magnitude')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.imshow(change_mask, cmap='gray')
plt.title('Change Mask')
plt.show()


