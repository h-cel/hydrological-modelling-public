# %% imports
import json

import geopandas as gpd
from conf import (
    AFSTROOMGEBIED_RAW_DIR,
    BBOX,
    DATASET_AFSTROOMGEBIED,
    EPSG_LAMBERT_72,
    WFS_ENDPOINT_AFSTROOMGEBIED,
)
from owslib.wfs import WebFeatureService

AFSTROOMGEBIED_RAW_DIR.mkdir(parents=True, exist_ok=True)
# %% Download Afstroomgebied data using WFS
wfs = WebFeatureService(WFS_ENDPOINT_AFSTROOMGEBIED, version="2.0.0")
wfs.contents[DATASET_AFSTROOMGEBIED]
crs_string = [
    crs
    for crs in wfs.contents[DATASET_AFSTROOMGEBIED].crsOptions
    if str(EPSG_LAMBERT_72) in str(crs)
][0]
response = wfs.getfeature(
    typename=DATASET_AFSTROOMGEBIED,
    bbox=BBOX,
    outputFormat="json",
    srsname=crs_string,
)
data_afstroomgebied = json.loads(response.read())
gdf_afstroomgebied = gpd.GeoDataFrame.from_features(
    data_afstroomgebied["features"], crs=EPSG_LAMBERT_72
)
gdf_afstroomgebied.to_file(AFSTROOMGEBIED_RAW_DIR / "afstroomgebied.shp")
