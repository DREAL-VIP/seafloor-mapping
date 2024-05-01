import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import fiona
import tempfile
import geopandas as gpd
from rasterio.mask import mask
from rasterio.crs import CRS
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.warp import reproject, Resampling
from tqdm import tqdm
from PIL import Image  # Import Pillow library
from rasterio import MemoryFile

# TIFF
tiff = r'C:\Users\jakem\source\repos\seafloor-mapping\data\BS_composite_10m.tif'
# Bathymetry tiff
bathy = r'C:\Users\jakem\source\repos\seafloor-mapping\data\Nahant_NH_bathy.tif'
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


            with rasterio.open(bathy) as bathy_src:
                raster_bounds = bathy_src.bounds

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
                    gdf = gdf.to_crs(bathy_src.crs)

                    # Clip to raster extent
                    gdf_clipped = gdf.cx[raster_bounds.left:raster_bounds.right, raster_bounds.bottom:raster_bounds.top]

                    # Extract shapes
                    shapes = gdf_clipped['geometry']

                    # Mask the bathymetry raster with the shapefile geometries
                    bout_image, bout_transform = mask(bathy_src, shapes, invert=False)
                    bathy_reprojected = np.zeros((bout_image.shape[0], out_image.shape[1], out_image.shape[2]), dtype=bout_image.dtype)
                    reproject(
                        bout_image,  # Source data
                        bathy_reprojected,  # Output buffer
                        src_transform=bout_transform,  # Source transform
                        src_crs=bathy_src.crs,  # Source CRS
                        dst_transform=out_transform,  # Destination transform
                        dst_crs=out_meta['crs'],  # Destination CRS
                        resampling=Resampling.bilinear  # Resampling method
                    )
                    # Append bathymetry band to the main raster bands
                    merged_bands = np.concatenate([out_image, bathy_reprojected], axis=0)


                    print(merged_bands.shape)
                    # Update metadata for the new bands
                    out_meta.update(count=out_image.shape[0] + 1)  # Increment band count

                    # Assuming merged_bands is the variable containing the merged bands
                    second_band = merged_bands[1, :, :]  # Extract the second band (indexing starts from 0)

                    # Plot the second band
                    plt.imshow(second_band, cmap='gray')  # Assuming grayscale colormap
                    plt.colorbar()  # Add colorbar for reference
                    plt.title('Second Band')  # Set title
                    plt.xlabel('X-axis')  # Set x-axis label
                    plt.ylabel('Y-axis')  # Set y-axis label
                    plt.show()

                        # Size of the patches
                    patch_size = 128

                        # Get raster shape
                    height, width = out_image.shape[-2:]
                    
                    #make dir if it doesnt exist
                    os.makedirs(output_dir, exist_ok=True)


                        # Iterate over the image and extract patches
                    for y in tqdm(range(0, height, patch_size)):
                        for x in range(0, width, patch_size):
                                # Define window for the patch
                            window = Window(x, y, min(patch_size, width - x), min(patch_size, height - y))

                                # Read patch from the merged raster
                            patch = merged_bands[:, window.col_off:window.col_off + window.width, window.row_off:window.row_off + window.height]
                            backscatterPatch = out_image[:, window.col_off:window.col_off + window.width, window.row_off:window.row_off + window.height]
    
                                # Check if patch contains valid data
                            if np.any(backscatterPatch):
                                    # Generate output file name based on patch position
                                output_file = os.path.join(output_dir, f"patch_{x}_{y}.tif")

                                    # Write patch to a new TIFF file
                                with rasterio.open(output_file, 'w', driver='GTiff', width=patch.shape[2], height=patch.shape[1], count=2,
                                                dtype=patch.dtype) as dst:
                                    dst.write(patch)
                                    print(f"Patched raster saved to: {output_file}")
                    else:
                        print("Dimensions of bathymetry band do not match the main raster.")

except Exception as e:
    print("An error occurred:", e)
