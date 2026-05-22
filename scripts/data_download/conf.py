import rootutils

# General paths
root_path = rootutils.find_root(search_from=__file__, indicator=".git")
data_dir = root_path / "data"
raw_data_dir = data_dir / "raw"
processed_data_dir = data_dir / "processed"

# DTM info
DATASET_DTM = "DHMVII_DTM_1m"  # DHMVI_DTM_5m (outdated)
dtm_raw_dir = raw_data_dir / "DTM"
dtm_processed_dir = processed_data_dir / "DTM"
DTM_SPATIAL_RESOLUTION = 1.0  # in meters
DTM_SPATIAL_RESOLUTION_UPSCALED = 10.0  # in meters
CRS = "http://www.opengis.net/def/crs/EPSG/0/31370"
XMIN, XMAX, YMIN, YMAX = 98_000, 116_000, 160_000, 180_000  # extent in m (EPSG:31370)
NO_DATA_VALUE_DTM = -9999.0
WCS_ENDPOINT_DTM = "https://geo.api.vlaanderen.be/dhmv/wcs"

# Meteorology station info
STATION_ID_MAARKE_KERKEM = "P06_014"


# Discharge station info
STATION_ID_NEDERZWALM = "L06_342"
PRECIP_CATCHMENT_LONGNAME = "Precipitation of catchment"
PRECIP_CATCHMENT_TS_NAME = "Rro.DagTot"
START_YEAR = 2009
END_YEAR = 2025
