import tifffile
import numpy as np
import rasterio
import rasterio.features
import rasterio.warp
from rasterio.plot import show

bathymetery_path = '../bathymetery/NAVD88_HS_30m.tif'
backscatter_path = '../backscatter/BS_composite_10m.tif'


with rasterio.open(backscatter_path) as dataset:

    # Read the dataset's valid data mask as a ndarray.
    mask = dataset.dataset_mask()
    print(dataset.count, dataset.width, dataset.height)
    show(dataset.read(1))

with rasterio.open(bathymetery_path) as dataset:

    # Read the dataset's valid data mask as a ndarray.
    mask = dataset.dataset_mask()
    print(dataset.count, dataset.width, dataset.height)
    show(dataset.read(1))
