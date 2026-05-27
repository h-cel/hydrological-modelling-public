import sys

import rootutils
from loguru import logger

LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level}</level> - <blue>{file.name}:{line}</blue> - <white>{message}</white>"

logger.remove()
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    colorize=True,
)

# General paths
ROOT_PATH = rootutils.find_root(search_from=__file__, indicator=".git")
DATA_DIR = ROOT_PATH / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DTM_RAW_DIR = RAW_DATA_DIR / "digital_terrain_model"
PRECIPITATION_RAW_DIR = RAW_DATA_DIR / "precipitation"
DISCHARGE_RAW_DIR = RAW_DATA_DIR / "discharge"
POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR = RAW_DATA_DIR / "potential_evapotranspiration"
VLAAMSE_HYDROGRAFISCHE_ATLAS_RAW_DIR = RAW_DATA_DIR / "vlaamse_hydrografische_atlas"
AFSTROOMGEBIED_RAW_DIR = RAW_DATA_DIR / "afstroomgebied"

# DTM info
DATASET_DTM = "DHMVII_DTM_1m"  # DHMVI_DTM_5m (outdated)
DTM_SPATIAL_RESOLUTION = 1.0  # in meters
CRS = "http://www.opengis.net/def/crs/EPSG/0/31370"
XMIN, XMAX, YMIN, YMAX = 98_000, 116_000, 160_000, 180_000  # extent in m (EPSG:31370)
NO_DATA_VALUE_DTM = -9999.0
WCS_ENDPOINT_DTM = "https://geo.api.vlaanderen.be/dhmv/wcs"
EPSG_LAMBERT_72 = 31370
TILE_SIZE = 2000  # in meters, one side of the requested tile
FILENAME_DTM = f"{DATASET_DTM}.tif"

# Vlaamse Hydrografishe Atlas (VHA)
WFS_ENDPOINT_VHA = "https://geo.api.vlaanderen.be/VHAWaterlopen/wfs"
DATASET_VHA = "VHAWaterlopen:VHAG"
BBOX = (XMIN, YMIN, XMAX, YMAX)  # in m (EPSG:31370)
FILENAME_VHA = "vlaamse_hydrografische_atlas.shp"

# Afstroomgebied
WFS_ENDPOINT_AFSTROOMGEBIED = (
    "https://geo.api.vlaanderen.be/Oppervlaktewaterlichamen/wfs"
)
DATASET_AFSTROOMGEBIED = "Oppervlaktewaterlichamen:AfstrZonA0"
FILENAME_AFSTROOMGEBIED = "afstroomgebied.shp"


# Waterinfo variables
TIMESPACING_DICT = {"P1D": "daily"}
DAILY_AGG = "Day"
TOTAL_AGG = "Total"
MEAN_AGG = "Mean"
FILENAME_WATERINFO_TEMPLATE = "{variable}_{station_id}_{time_spacing}.csv"
FILENAME_WATERINFO_META_TEMPLATE = "{variable}_meta_{station_id}_{time_spacing}.csv"

# Pluvio station info
STATION_ID_MAARKE_KERKEM = "P06_014"
PRECIPITATION_LONGNAME = "Precipitation"

# Meteo station info
STATION_ID_WAREGEM = "ME05_019"
POTENTIAL_EVAPOTRANSPIRATION_LONGNAME = "Potential Evapotranspiration"
POTENTIAL_EVAPOTRANSPIRATION_SUFFIX = "Penman"

# Discharge station info
STATION_ID_NEDERZWALM = "L06_342"
PRECIPITATION_CATCHMENT_LONGNAME = "Precipitation of catchment"
PRECIPITATION_CATCHMENT_SUFFIX = "(rro)"
DISCHARGE_LONGNAME = "River Discharge"
