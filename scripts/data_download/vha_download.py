# %% Imports
import json

import geopandas as gpd
from conf import (
    BBOX,
    DATASET_VHA,
    EPSG_LAMBERT_72,
    FILENAME_VHA,
    VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR,
    WFS_ENDPOINT_VHA,
    logger,
)
from owslib.wfs import WebFeatureService


def main():
    VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    # %% Download VHA data using WFS
    logger.info(f"Downloading {DATASET_VHA} via WFS from {WFS_ENDPOINT_VHA}")
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
    out_path = VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR / FILENAME_VHA
    gdf_vha.to_file(out_path)
    logger.info(f"{DATASET_VHA} saved to {out_path}")


if __name__ == "__main__":
    main()
