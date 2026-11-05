# AGENTS.md file hydrological modelling 

## Setup

- This repository uses conda for environment management.
- There are two environments: `environment.yml` (light student env, `hydromod_env`, sufficient for `quarto render`) and `environment_dev.yml` (`hydromod_env_dev`, needed for `scripts/data_download`, `scripts/data_process` and the GRASS Python route).
- For running python code, you can use the command `conda activate <env_name>` to activate the environment or use `conda run -n <env_name> python <script.py>` to run a script without activating the environment.

## Quarto 

- Consider using the [quarto-authoring skill](https://github.com/posit-dev/skills/tree/main/quarto/quarto-authoring)
- Make sure to activate the conda environment before running quarto commands.
- `quarto render` is the most important command to render the full project. 

