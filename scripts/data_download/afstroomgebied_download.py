# %% imports
import json

import geopandas as gpd
from conf import (
    AFSTROOMGEBIED_RAW_DIR,
    BBOX,
    DATASET_AFSTROOMGEBIED,
    EPSG_LAMBERT_72,
    FILENAME_AFSTROOMGEBIED,
    WFS_ENDPOINT_AFSTROOMGEBIED,
    logger,
)
from owslib.wfs import WebFeatureService


def main():
    AFSTROOMGEBIED_RAW_DIR.mkdir(parents=True, exist_ok=True)
    # %% Download Afstroomgebied data using WFS
    logger.info(
        f"Downloading {DATASET_AFSTROOMGEBIED} via WFS from {WFS_ENDPOINT_AFSTROOMGEBIED}"
    )
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
    out_path = AFSTROOMGEBIED_RAW_DIR / FILENAME_AFSTROOMGEBIED
    gdf_afstroomgebied.to_file(out_path)
    logger.info(f"{DATASET_AFSTROOMGEBIED} saved to {out_path}")


if __name__ == "__main__":
    main()
