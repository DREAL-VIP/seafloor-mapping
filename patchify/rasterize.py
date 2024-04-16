import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import fiona
import tempfile
import geopandas as gpd
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.crs import CRS
from rasterio.windows import Window
from tqdm import tqdm

# TIFF
tiff = r'C:\Users\jakem\source\repos\seafloor-mapping\data\BS_composite_10m.tif'
# Shapefile
shape = r'C:\Users\jakem\source\repos\seafloor-mapping\data\Nahant_NH_sedcover.shp'
# Output directory
output_dir = r'C:\Users\jakem\source\repos\seafloor-mapping\output'

# Generate a temporary file path
temp_file_path = tempfile.NamedTemporaryFile(suffix='.tif').name

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
            
            # Set CRS for GeoDataFrame
            gdf.crs = CRS.from_epsg(4326)  # Assuming EPSG code for the CRS
            
            # Reproject to raster CRS
            gdf = gdf.to_crs(src.crs)

            # Clip to raster extent
            gdf_clipped = gdf.cx[raster_bounds.left:raster_bounds.right, raster_bounds.bottom:raster_bounds.top]

            # Extract shapes
            shapes = gdf_clipped['geometry']

            # Check if shapes list is empty
            if shapes.empty:
                print("No valid geometries found in the shapefile.")
            else:
                # Mask the raster using the clipped shapefile geometries
                out_image, out_transform = mask(src, shapes, invert=False)
                out_meta = src.meta

                # Plot the masked image
                plt.figure(figsize=(8, 8))
                plt.imshow(out_image[0], cmap='viridis')  # Assuming it's a single-band image
                plt.colorbar()
                plt.show()

                # Size of the patches
                patch_size = 256

                # Create the output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)

                # Get raster shape
                height, width = out_image.shape[-2:]

                # Iterate over the image and extract patches
                for y in tqdm(range(0, height, patch_size)):
                    for x in range(0, width, patch_size):
                        # Define window for the patch
                        window = Window(x, y, min(patch_size, width - x), min(patch_size, height - y))

                        # Read patch from the raster
                        patch = out_image[:, window.col_off:window.col_off + window.width, window.row_off:window.row_off + window.height]

                        # Check if patch contains valid data
                        if np.any(patch):
                            # Generate output file name based on patch position
                            output_file = os.path.join(output_dir, f"patch_{x}_{y}.tif")

                            # Write patch to a new TIFF file
                            with rasterio.open(output_file, 'w', driver='GTiff', width=patch.shape[2], height=patch.shape[1], count=1,
                                               dtype=patch.dtype) as dst:
                                dst.write(patch)

except Exception as e:
    print("An error occurred:", e)
