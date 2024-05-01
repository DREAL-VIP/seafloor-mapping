import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.plot import show
import matplotlib.patches as mpatches
import cv2
from PIL import Image
import numpy as np
# Path to the original TIFF patch
patch = r"\patch_1408_768."
original_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\output'+ patch + "tif"
# Path to the shapefile patch
shapefile_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\shapefile_output'+patch + "png"

# Define sediment colors within the 0-1 range
sediment_colors = {
    'S': (1.0, 1.0, 0.0),    # Yellow for Sand
    'G': (0.5, 0.0, 0.5),    # Purple for Gravel
    'R': (0.5, 0.5, 0.5),    # Gray for Rock
    'M': (0.0, 0.0, 1.0),    # Blue for Mud
    'Sg': (1.0, 0.647, 0.0), # Orange for Sand and Gravel
    'Sr': (1.0, 0.753, 0.796),# Pink for Sand and Rock
    'Sm': (0.0, 1.0, 1.0),   # Cyan for Sand and Mud
    'Gs': (0.0, 1.0, 0.0),   # Green for Gravel and Sand
    'Gr': (1.0, 0.0, 0.0),   # Red for Gravel and Rock
    'Gm': (1.0, 0.271, 0.0), # Orange-Red for Gravel and Mud
    'Ms': (0.0, 0.502, 0.502),# Teal for Mud and Sand
    'Mg': (0.0, 1.0, 0.502),  # Bluish-Green for Mud and Gravel
    'Mr': (0.502, 0.0, 0.0),  # Maroon for Mud and Rock
    'Rs': (0.753, 0.753, 0.753),# Light Gray for Rock and Sand
    'Rg': (0.502, 0.0, 1.0),  # Purple-Blue for Rock and Gravel
    'Rm': (0.0, 0.0, 0.502),  # Navy for Rock and Mud
}

try:
    # Open the original patch
    with rasterio.open(original_patch_file) as src_original:
        # Read the original patch as a numpy array
        backscatter_data = src_original.read(1) 
        bathymetry_data = src_original.read(2) 

    # Open the shapefile patch
        shapefile_patch_data = plt.imread(shapefile_patch_file)
        shapefile_patch_data = np.moveaxis(shapefile_patch_data, -1, 0)  # Move the channel axis to the first position


        # Plot both patches side by side
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))  # Adjust the number of subplots and figure size as needed

        # Plot the original backscatter patch
        show(backscatter_data, ax=axs[0], cmap='gray')
        axs[0].set_title('Backscatter Patch')
        axs[0].set_xlabel('X')
        axs[0].set_ylabel('Y')
        axs[0].grid(False)

        # Plot the original bathymetry patch
        show(bathymetry_data, ax=axs[1], cmap='terrain')  # Adjust the colormap as needed
        axs[1].set_title('Bathymetry Patch')
        axs[1].set_xlabel('X')
        axs[1].set_ylabel('Y')
        axs[1].grid(False)

        # Plot the shapefile patch
        show(shapefile_patch_data, ax=axs[2])
        axs[2].set_title('Shapefile Patch')
        axs[2].set_xlabel('X')
        axs[2].set_ylabel('Y')
        axs[2].grid(False)

        plt.show()

        # Create legend for sediment types and colors
        #legend_patches = [mpatches.Patch(color=color, label=sed_type) for sed_type, color in sediment_colors.items()]
        #plt.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=4)
        
        plt.tight_layout()
        #img = cv2.imread(original_patch_file,)
        #print(img)
        #cv2.imshow('',img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        #cv2.waitKey(1)

except Exception as e:
    print("An error occurred:", e)
