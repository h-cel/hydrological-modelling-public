# Objective: allows import from the conf.py as defined in the data_download folder
import os
from importlib.machinery import SourceFileLoader

import rootutils

root_path = rootutils.find_root(search_from=__file__, indicator=".git")
conf_module = SourceFileLoader(
    "conf", os.path.join(root_path, "scripts", "data_download", "conf.py")
).load_module()
