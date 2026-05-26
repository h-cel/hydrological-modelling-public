# Objective: allows import from the conf.py as defined in the data_download folder
import os
from importlib.machinery import SourceFileLoader

import rootutils

root_path = rootutils.find_root(search_from=__file__, indicator=".git")
conf_module = SourceFileLoader(
    "conf", os.path.join(root_path, "scripts", "data_download", "conf.py")
).load_module()

# DTM info
DTM_SPATIAL_RESOLUTION_UPSCALED = 10.0  # in meters

# Meteorological data info
EP_MINIMUM = -1.0  # mm/day, below this value is not realistic data
EP_TRESHOLD = (
    0.0  # mm/day, for simplicity set data below threshold (above minimum) to zero
)
