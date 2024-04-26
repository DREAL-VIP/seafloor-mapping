import rasterio
import matplotlib.pyplot as plt
import geopandas as gpd
from rasterio.plot import show
import matplotlib.patches as mpatches
import cv2
# Path to the original TIFF patch
original_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\output\patch_5888_2560.tif'
# Path to the shapefile patch
shapefile_patch_file = r'C:\Users\jakem\source\repos\seafloor-mapping\shapefile_output\mask_5888_2560.tif'

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

        # Create legend for sediment types and colors
        legend_patches = [mpatches.Patch(color=color, label=sed_type) for sed_type, color in sediment_colors.items()]
        plt.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=4)
        
        plt.tight_layout()
        #plt.show()
        img = cv2.imread(original_patch_file,)
        print(img)
        cv2.imshow('',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

except Exception as e:
    print("An error occurred:", e)
