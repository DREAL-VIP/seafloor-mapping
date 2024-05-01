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
from PIL import Image  # Import Pillow library

# TIFF
tiff = r'C:\Users\jakem\source\repos\seafloor-mapping\data\Nahant_NH_bathy.tif'
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
        bands = src.read()
        print(bands.shape)
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
                plt.imshow(out_image[0], cmap='grey')  # Assuming it's a single-band image
                plt.colorbar()
                plt.show()

except Exception as e:
    print("An error occurred:", e)
