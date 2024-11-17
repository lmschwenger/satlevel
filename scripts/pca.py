import os
import numpy as np
from osgeo import gdal
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def load_bands(band_files):
    bands = []
    for band_file in band_files:
        dataset = gdal.Open(band_file)
        band_data = dataset.ReadAsArray()  # Read the band as a 2D numpy array
        bands.append(band_data)
    return np.stack(bands, axis=2)  # Stack bands along the third dimension


# Example usage
files = [
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B02_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B03_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B04_(Raw).tiff",
    r"C:\rs_dev\change_detection\case_1_wadden\imgs\20240921\2024-09-21-00_00_2024-09-21-23_59_Sentinel-2_L2A_B08_(Raw).tiff"
    ]  # List of band files
image_stack = load_bands(files)

# Get the shape of the image
rows, cols, num_bands = image_stack.shape

# Reshape the data for PCA: (pixels, bands)
image_reshaped = image_stack.reshape((rows * cols, num_bands))

# Initialize PCA
pca = PCA(n_components=num_bands)  # Set the number of components equal to the number of bands

# Fit PCA to the data and transform
principal_components = pca.fit_transform(image_reshaped)

# Reshape the principal components back to the original image shape
pca_images = principal_components.reshape((rows, cols, num_bands))

# Plot the first three principal components
plt.figure(figsize=(12, 4))
for i in range(3):
    plt.subplot(1, 3, i + 1)
    plt.imshow(pca_images[:, :, i], cmap='gray')
    plt.title(f'Principal Component {i + 1}')
    plt.axis('off')
plt.show()
