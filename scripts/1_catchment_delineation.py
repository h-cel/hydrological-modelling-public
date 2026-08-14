# %% Imports
import shutil
import subprocess
import sys

import rootutils

# Robust access to functions from helper_functions.py
ROOT_PATH = rootutils.find_root(search_from=__file__, indicator=".git")
sys.path.append(str(ROOT_PATH / "scripts"))

from helper_functions import find_grass_python_path

# Add GRASS GIS Python path to sys.path
grass_python_path = find_grass_python_path()
if grass_python_path is not None:
    sys.path.append(grass_python_path)
    import grass.script as gs
    from grass.tools import Tools
else:
    raise RuntimeError(
        "Could not find GRASS GIS Python path. Make sure GRASS GIS is installed and "
        "accessible. Functions relying on GRASS GIS will not work."
    )


grass_project_dir = ROOT_PATH / "grass_project"

# %% Create a new GRASS project and session every time the script is run
if grass_project_dir.exists():
    shutil.rmtree(grass_project_dir)
gs.create_project(path=grass_project_dir, epsg=31370)

session = gs.setup.init(grass_project_dir)
tools = Tools(session=session)

# %% Solutions
