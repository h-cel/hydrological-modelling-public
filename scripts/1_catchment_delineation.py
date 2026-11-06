# %% Imports
import sys

import geopandas as gpd
import pyflwdir
import rasterio.features
import rioxarray
import rootutils

# Robust access to functions from scripts/
ROOT_PATH = rootutils.find_root(search_from=__file__, indicator="pyproject.toml")
sys.path.append(str(ROOT_PATH / "scripts"))

# %% Load data

da_dtm = rioxarray.open_rasterio(...).isel(
    band=0
)  # Select the first band if there are multiple bands
elevtn = da_dtm.values
nodata = da_dtm.nodata
transform = da_dtm.rio.transform()
crs = da_dtm.rio.crs
gdf_river = gpd.read_file(...)
gdf_watershed_reference = gpd.read_file(...)

# %% Check missing values in the DTM and fill if needed

# %% Flow directions and accumulation with pyflwdir
# https://deltares.github.io/pyflwdir/
flw = pyflwdir.from_array(...)

# %% Find the point  with the highest accumulation on the river
shapes = gdf_river.to_crs(crs).geometry
arr_river = rasterio.features.rasterize(shapes=..., out_shape=..., transform=...)
idx_max = ...
x_max, y_max = flw.xy(...)

# %% Delineate the basin upstream of an outlet and vectorize

basins = flw.basins(xy=...)

list_vector_features_basins = list(
    rasterio.features.shapes(source=..., mask=..., connectivity=..., transform=...)
)

gdf_watershed = gpd.GeoDataFrame.from_features(..., crs=...)

# %% Repeat delineation for the other outlet point
