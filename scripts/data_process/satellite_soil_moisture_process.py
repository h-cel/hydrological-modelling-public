# %% Imports
import geopandas as gpd
import numpy as np
import xarray as xr
from conf import (
    CATCHMENT_INFO_PROCESSED_DIR,
    CATCHMENT_NAME,
    FILENAME_AFSTROOMGEBIED,
    MIN_COVERAGE_RATIO,
    SATELLITE_SOIL_MOISTURE_RAW_DIR,
)

if __name__ == "__main__":
    # %% Read in
    ds = xr.open_mfdataset(
        SATELLITE_SOIL_MOISTURE_RAW_DIR.glob("*/*.nc"),
        decode_coords="all",
        chunks="auto",
    ).rename({"t": "time", "x": "lon", "y": "lat"})

    gdf = gpd.read_file(CATCHMENT_INFO_PROCESSED_DIR / FILENAME_AFSTROOMGEBIED)
    gdf_catchment = gdf[
        gdf["A0NAAM"].str.contains(CATCHMENT_NAME, case=False, na=False)
    ]

    # %% Create reference DataArray with full spatial coverage
    da_ref = ds["ssm"].isel(time=0).copy()
    da_ref.values = np.random.rand(*da_ref.shape)  # Fill with random values

    # %% Clip surface soil moisture data to catchment area
    ds_clipped = ds.rio.clip(
        gdf_catchment.geometry.values, gdf_catchment.crs, all_touched=True
    )
    da_ref_clipped = da_ref.rio.clip(
        gdf_catchment.geometry.values, gdf_catchment.crs, all_touched=True
    )

    # %% Only keep pixels with coverage more than the minimum coverage ratio
    nr_pixels_full_coverage = da_ref_clipped.count().item()
    nr_pixels_min = int(np.ceil(MIN_COVERAGE_RATIO * nr_pixels_full_coverage))
    nr_pixels_clipped = ds_clipped["ssm"].count(dim=["lat", "lon"])
    bool_time_steps_to_keep = nr_pixels_clipped >= nr_pixels_min
    ds_clipped_filtered = ds_clipped.sel(time=bool_time_steps_to_keep)
