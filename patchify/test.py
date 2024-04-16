import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.plot import show

# Path to the original TIFF patch
original_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\output\patch_6144_2816.tif'
# Path to the shapefile patch
shapefile_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\shapefile_output\patch_6144_2816.tif'

try:
    # Open the original patch
    with rasterio.open(original_patch_file) as src_original:
        # Read the original patch as a numpy array
        original_patch_data = src_original.read(1)  # Assuming it's a single-band image

    # Open the shapefile patch
    with rasterio.open(shapefile_patch_file) as src_shapefile:
        # Plot both patches side by side
        fig, axs = plt.subplots(1, 2, figsize=(12, 6))

        # Plot the original patch
        show(original_patch_data, ax=axs[0], cmap='gray')
        axs[0].set_title('Original Patch')
        axs[0].set_xlabel('X')
        axs[0].set_ylabel('Y')
        axs[0].grid(False)

        # Plot the shapefile patch and color it based on the 'sed_type' attribute
        show(src_shapefile, ax=axs[1])
        axs[1].set_title('Shapefile Patch')
        axs[1].set_xlabel('X')
        axs[1].set_ylabel('Y')
        axs[1].grid(False)

        plt.tight_layout()
        plt.show()

except Exception as e:
    print("An error occurred:", e)
