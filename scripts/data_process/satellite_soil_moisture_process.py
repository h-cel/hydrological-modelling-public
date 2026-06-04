# %% Imports
import geopandas as gpd
import numpy as np
import rioxarray
import xarray as xr
from conf import (
    CATCHMENT_INFO_PROCESSED_DIR,
    CATCHMENT_NAME,
    FILENAME_AFSTROOMGEBIED,
    FILENAME_SATELLITE_SOIL_MOISTURE,
    MAX_PCT_RISE_PER_DAY,
    MIN_COVERAGE_RATIO,
    MIN_PCT_DROP_PER_DAY,
    SATELLITE_SOIL_MOISTURE_PROCESSED_DIR,
    SATELLITE_SOIL_MOISTURE_RAW_DIR,
    VARIABLE_NAME_NOISE,
    VARIABLE_NAME_SATELLITE_SOIL_MOISTURE,
    logger,
)

SATELLITE_SOIL_MOISTURE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
rioxarray.set_options(convention=rioxarray.enum.Convention.CF)


# %% Main function
def main():
    # %% Read in
    ds = xr.open_mfdataset(
        SATELLITE_SOIL_MOISTURE_RAW_DIR.glob("*/*.nc"),
        decode_coords="all",
        chunks="auto",
    ).rename({"t": "time", "x": "lon", "y": "lat"})
    # Set CRS properly
    crs_ssm = ds.rio.crs
    ds = ds.astype(np.float32).drop_vars("crs").rio.write_crs(crs_ssm)

    gdf = gpd.read_file(CATCHMENT_INFO_PROCESSED_DIR / FILENAME_AFSTROOMGEBIED)
    gdf_catchment = gdf[
        gdf["A0NAAM"].str.contains(CATCHMENT_NAME, case=False, na=False)
    ]

    # %% Create reference DataArray with full spatial coverage
    da_ref = ds[VARIABLE_NAME_SATELLITE_SOIL_MOISTURE].isel(time=0).copy()
    da_ref.values = np.random.rand(*da_ref.shape)  # Fill with random values

    # %% Clip surface soil moisture data to catchment area
    logger.info(
        f"Clipping surface soil moisture data to catchment area: {CATCHMENT_NAME}"
    )
    ds_clipped = ds.rio.clip(
        gdf_catchment.geometry.values, gdf_catchment.crs, all_touched=True
    )
    da_ref_clipped = da_ref.rio.clip(
        gdf_catchment.geometry.values, gdf_catchment.crs, all_touched=True
    )
    logger.info("Saving clipped surface soil moisture data to a NetCDF file.")
    ds_clipped.to_netcdf(
        SATELLITE_SOIL_MOISTURE_PROCESSED_DIR
        / FILENAME_SATELLITE_SOIL_MOISTURE.replace(".csv", "_unfiltered.nc")
    )

    # %% Only keep pixels with coverage more than the minimum coverage ratio
    logger.info(
        f"Removing time steps with less than {MIN_COVERAGE_RATIO:.0%} spatial coverage."
    )
    nr_pixels_full_coverage = da_ref_clipped.count().item()
    nr_pixels_min = int(np.ceil(MIN_COVERAGE_RATIO * nr_pixels_full_coverage))
    nr_pixels_clipped = ds_clipped[VARIABLE_NAME_SATELLITE_SOIL_MOISTURE].count(
        dim=["lat", "lon"]
    )
    bool_time_steps_to_keep = nr_pixels_clipped >= nr_pixels_min
    ds_clipped_filtered = ds_clipped.sel(time=bool_time_steps_to_keep)
    nr_pixels_filtered = nr_pixels_clipped.sel(time=bool_time_steps_to_keep)

    # %% Average surface soil moisture over catchment area
    logger.info("Averaging surface soil moisture over catchment area.")
    da_spatial_avg_ssm = (
        ds_clipped_filtered[VARIABLE_NAME_SATELLITE_SOIL_MOISTURE]
        .mean(dim=["lat", "lon"], skipna=True)
        .compute()
    )
    da_spatial_avg_noise = (
        1
        / nr_pixels_filtered
        * np.sqrt(
            (ds_clipped_filtered[VARIABLE_NAME_NOISE] ** 2).sum(
                dim=["lat", "lon"], skipna=True
            )
        )
    ).compute()
    ds_spatial_avg = xr.Dataset({
        VARIABLE_NAME_SATELLITE_SOIL_MOISTURE: da_spatial_avg_ssm,
        VARIABLE_NAME_NOISE: da_spatial_avg_noise,
    })

    # %% Filter out too large fluctuations
    logger.info("Filtering out unrealistic fluctuations in surface soil moisture")
    time_diff_days = ds_spatial_avg["time"].diff(dim="time").dt.total_seconds() / 86400
    pct_change_per_day = (
        ds_spatial_avg[VARIABLE_NAME_SATELLITE_SOIL_MOISTURE].diff(dim="time")
        / time_diff_days
    ).reindex(time=ds_spatial_avg.time, fill_value=0)
    flag_outliers = (pct_change_per_day < MIN_PCT_DROP_PER_DAY) | (
        pct_change_per_day > MAX_PCT_RISE_PER_DAY
    ).compute()
    ds_spatial_avg_filtered = ds_spatial_avg.where(~flag_outliers, drop=True)

    # %% Save to csv
    path_save = SATELLITE_SOIL_MOISTURE_PROCESSED_DIR / FILENAME_SATELLITE_SOIL_MOISTURE
    logger.info(f"Saving processed surface soil moisture data to {path_save}")
    ds_spatial_avg_filtered.to_dataframe().drop(["spatial_ref"], axis=1).to_csv(
        path_save
    )


# %% Run main
if __name__ == "__main__":
    main()
