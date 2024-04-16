import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import fiona
import tempfile
import geopandas as gpd
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.windows import Window
from rasterio.crs import CRS 
from tqdm import tqdm
from rasterio.enums import ColorInterp

# TIFF
tiff = r'C:\Users\jakem\source\repos\seafloor-mapping\data\BS_composite_10m.tif'
# Shapefile
shape = r'C:\Users\jakem\source\repos\seafloor-mapping\data\Nahant_NH_sedcover.shp'
# Output directory for raster image patches
raster_output_dir = r'C:\Users\jakem\source\repos\seafloor-mapping\shapefile_output'

# Generate a temporary file path
temp_file_path = tempfile.NamedTemporaryFile(suffix='.tif').name

# Define colors for each sediment type
sediment_colors = {
    'S': (255, 255, 0),  # Yellow for Sand
    'G': (128, 0, 128),   # Purple for Gravel
    'R': (128, 128, 128), # Gray for Rock
    'M': (0, 0, 255),     # Blue for Mud
    'Sg': (255, 165, 0),  # Orange for Sand and Gravel
    'Sr': (255, 192, 203),# Pink for Sand and Rock
    'Sm': (0, 255, 255),  # Cyan for Sand and Mud
    'Gs': (0, 255, 0),    # Green for Gravel and Sand
    'Gr': (255, 0, 0),    # Red for Gravel and Rock
    'Gm': (255, 69, 0),   # Orange-Red for Gravel and Mud
    'Ms': (0, 128, 128),  # Teal for Mud and Sand
    'Mg': (0, 255, 128),  # Bluish-Green for Mud and Gravel
    'Mr': (128, 0, 0),    # Maroon for Mud and Rock
    'Rs': (192, 192, 192),# Light Gray for Rock and Sand
    'Rg': (128, 0, 255),  # Purple-Blue for Rock and Gravel
    'Rm': (0, 0, 128),    # Navy for Rock and Mud
}

try:
    # Open TIFF raster
    with rasterio.open(tiff) as src:
        # Read raster bounds
        raster_bounds = src.bounds
        # Check if raster bounds are empty
        if not raster_bounds:
            print("Raster bounds are empty. Check if the raster file is valid.")
        else:
            print("Raster bounds:", raster_bounds)

            # Open shapefile
            gdf = gpd.read_file(shape)
            
            # Add sediment type columns
            print(gdf.head)

            # Set geometry column
            gdf = gdf.set_geometry('geometry')
            # Set CRS for GeoDataFrame
            gdf.crs = CRS.from_epsg(4326)  # Assuming EPSG code for the CRS
            
            # Reproject to raster CRS
            gdf = gdf.to_crs(src.crs)

            # Clip to raster extent
            gdf_clipped = gdf.cx[raster_bounds.left:raster_bounds.right, raster_bounds.bottom:raster_bounds.top]
            
            # Reset index of the GeoDataFrame
            gdf_clipped_reset = gdf_clipped.reset_index(drop=True)

            # Create a single raster file where each sediment type is represented by a unique color
            combined_mask = np.zeros((src.height, src.width), dtype=np.uint8)
            colors = {}

            for sed_type, color in sediment_colors.items():
                # Create a mask for the sediment type
                mask_shape = rasterio.features.geometry_mask(
                    gdf_clipped_reset[gdf_clipped_reset['sed_type'] == sed_type]['geometry'],
                    out_shape=(src.height, src.width),
                    transform=src.transform,
                    invert=True
                ).astype(np.uint8)  # Convert dtype to uint8

                # Assign a unique value to the mask
                combined_mask[mask_shape == 1] = len(colors) + 1
                # Save the color associated with the sediment type
                colors[len(colors) + 1] = color

            # Write the combined mask to a temporary file
            with rasterio.open(temp_file_path, 'w', driver='GTiff', width=src.width, height=src.height, count=1,
                               dtype=combined_mask.dtype, crs=src.crs, transform=src.transform) as dst:
                dst.write(combined_mask, 1)

            # Plot the combined mask with colors based on sediment types
            plt.figure(figsize=(8, 8))
            plt.imshow(combined_mask, cmap='viridis', vmin=1, vmax=len(colors) + 1)
            plt.title("Combined Mask with Colors Based on Sediment Types")
            plt.show()

            # Size of the patches
            patch_size = 256

            # Create the output directory if it doesn't exist
            os.makedirs(raster_output_dir, exist_ok=True)

            # Get raster shape
            height, width = combined_mask.shape

            # Iterate over the image and extract patches
            for y in tqdm(range(0, height, patch_size)):
                for x in range(0, width, patch_size):
                    # Define window for the patch
                    window = Window(x, y, min(patch_size, width - x), min(patch_size, height - y))

                    # Read patch from the combined mask
                    patch = combined_mask[window.col_off:window.col_off + window.width,
                                          window.row_off:window.row_off + window.height]

                    # Check if patch contains valid data
                    if np.any(patch):
                        # Generate output file name based on patch position
                        output_file = os.path.join(raster_output_dir, f"patch_{x}_{y}.tif")

                        # Apply colors to the patch
                        colored_patch = np.zeros((patch.shape[0], patch.shape[1], 3), dtype=np.uint8)
                        for value, color in colors.items():
                            colored_patch[patch == value] = color

                        # Write patch to a new TIFF file
                        with rasterio.open(output_file, 'w', driver='GTiff', width=patch.shape[1], height=patch.shape[0], count=3,
                                           dtype=np.uint8, crs=src.crs, transform=src.transform) as dst:
                            dst.write(colored_patch.transpose(2, 0, 1))

except Exception as e:
    print("An error occurred:", e)
