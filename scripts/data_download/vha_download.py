# %% Imports
import json

import geopandas as gpd
from conf import (
    BBOX,
    DATASET_VHA,
    EPSG_LAMBERT_72,
    VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR,
    WFS_ENDPOINT_VHA,
)
from owslib.wfs import WebFeatureService

VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR.mkdir(parents=True, exist_ok=True)
# %% Download VHA data using WFS
wfs = WebFeatureService(WFS_ENDPOINT_VHA, version="2.0.0")
crs_string = [
    crs
    for crs in wfs.contents[DATASET_VHA].crsOptions
    if str(EPSG_LAMBERT_72) in str(crs)
][0]
response = wfs.getfeature(
    typename=DATASET_VHA,
    bbox=BBOX,
    outputFormat="json",
    srsname=crs_string,
)
data_vha = json.loads(response.read())
gdf_vha = gpd.GeoDataFrame.from_features(data_vha["features"], crs=EPSG_LAMBERT_72)
gdf_vha.to_file(VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR / "VHA.shp")
