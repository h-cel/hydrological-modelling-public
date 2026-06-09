# %% Imports
import shutil
import subprocess
import sys

import rootutils

sys.path.append(
    subprocess.check_output(["grass", "--config", "python_path"], text=True).strip()
)

import grass.script as gs
from grass.tools import Tools

ROOT_PATH = rootutils.find_root(search_from=__file__, indicator=".git")
grass_project_dir = ROOT_PATH / "grass_project"

# %% Create a new GRASS project and session every time the script is run
if grass_project_dir.exists():
    shutil.rmtree(grass_project_dir)
gs.create_project(path=grass_project_dir, epsg=31370)

session = gs.setup.init(grass_project_dir)
tools = Tools(session=session)
