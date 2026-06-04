# Objective: allows import from the conf.py as defined in the data_download folder
import os
from importlib.machinery import SourceFileLoader

import rootutils

root_path = rootutils.find_root(search_from=__file__, indicator=".git")
conf_module = SourceFileLoader(
    "conf", os.path.join(root_path, "scripts", "data_download", "conf.py")
).load_module()

# General paths
DATA_DIR = conf_module.DATA_DIR
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DTM_PROCESSED_DIR = PROCESSED_DATA_DIR / "digital_terrain_model"
FORCINGS_DISCHARGE_PROCESSED_DIR = PROCESSED_DATA_DIR / "forcings_discharge"
CATCHMENT_INFO_PROCESSED_DIR = PROCESSED_DATA_DIR / "catchment_info"
SATELLITE_SOIL_MOISTURE_PROCESSED_DIR = PROCESSED_DATA_DIR / "satellite_soil_moisture"

# DTM info
DTM_SPATIAL_RESOLUTION_UPSCALED = 10.0  # in meters

# Forcings and discharge data info
FILENAME_FORCINGS_DISCHARGE = "forcings_discharge.csv"
FILENAME_FORCINGS_DISCHARGE_META = "forcings_discharge_meta.csv"
EP_MINIMUM = -1.0  # mm/day, below this value is not realistic data
EP_TRESHOLD = (
    0.0  # mm/day, for simplicity set data below threshold (above minimum) to zero
)
_half_window_size_climatology = 5  # days
WINDOW_SIZE_CLIMATOLOGY = 2 * _half_window_size_climatology + 1
METADATA_MAP = {
    "station_no": "id",
    "station_name": "name",
    "ts_unitsymbol": "unit",
    "station_longitude": "longitude",
    "station_latitude": "latitude",
    "station_local_x": "x",
    "station_local_y": "y",
}

# Catchment info
CATCHMENT_NAME = "ZWALM"

# Satellite soil moisture
FILENAME_SATELLITE_SOIL_MOISTURE = "satellite_soil_moisture.csv"
VARIABLE_NAME_SATELLITE_SOIL_MOISTURE = "ssm"
MIN_COVERAGE_RATIO = 0.90
MIN_PCT_DROP_PER_DAY = -7.5
MAX_PCT_RISE_PER_DAY = 15
