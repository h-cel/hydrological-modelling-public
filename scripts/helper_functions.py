import subprocess
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import rioxarray  # noqa: F401
import xarray as xr


def find_grass_python_path():
    for command in (
        ["grass", "--config", "python_path"],
        ["conda", "run", "grass", "--config", "python_path"],
    ):
        try:
            return subprocess.check_output(command, text=True).strip()
        except Exception:
            continue
    return None


grass_python_path = find_grass_python_path()
if grass_python_path is not None:
    sys.path.append(grass_python_path)
    import grass.script as gs
    import grass.script.array as ga
else:
    warnings.warn(
        "Could not find GRASS GIS Python path. Make sure GRASS GIS is installed and "
        "accessible. Functions relying on GRASS GIS might not work.",
        RuntimeWarning,
    )
    gs = None
    ga = None


def get_data_array_from_grass(raster_name: str) -> xr.DataArray:
    """
    Convert a GRASS raster to an xarray DataArray given its name in the GRASS session.

    Parameters
    ----------
    raster_name
        The name of the raster in the GRASS session.

    Returns
    -------
    da_raster
        The raster as an xarray DataArray with appropriate coordinates and dimensions.

    """
    raster_np_array = ga.array(raster_name)
    raster_info = gs.raster_info(raster_name)
    east_west_resolution = raster_info["ewres"]
    north_south_resolution = raster_info["nsres"]
    west_lim = raster_info["west"]
    east_lim = raster_info["east"]
    north_lim = raster_info["north"]
    south_lim = raster_info["south"]
    crs_dict = gs.parse_command("g.proj", format="wkt", flags="pf")
    crs_wkt = next(iter(crs_dict.keys()))
    x_coords = np.arange(
        west_lim + east_west_resolution / 2, east_lim, east_west_resolution
    )
    y_coords = np.arange(
        north_lim - north_south_resolution / 2, south_lim, -north_south_resolution
    )
    da_raster = xr.DataArray(
        raster_np_array,
        coords={"y": y_coords, "x": x_coords},
        dims=["y", "x"],
    )
    da_raster.rio.write_crs(crs_wkt, inplace=True)
    return da_raster


def plot_grass_raster(
    raster_name: str,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    interpolation: str = "auto",
    **kwargs,
):
    da_raster = get_data_array_from_grass(raster_name)
    if ax is None:
        fig, ax = plt.subplots(constrained_layout=True)
    da_raster.plot.imshow(ax=ax, interpolation=interpolation, **kwargs)
    fig.autofmt_xdate()
    return fig, ax
