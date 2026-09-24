# %% Imports
from itertools import combinations

import geopandas as gpd
import pandas as pd
import shapely
import shapely.ops
from conf import (
    CATCHMENT_A0CODE,
    CATCHMENT_INFO_PROCESSED_DIR,
    DISCHARGE_LONGNAME,
    DISCHARGE_RAW_DIR,
    EP_MINIMUM,
    EP_TRESHOLD,
    EPSG_LAMBERT_72,
    FILENAME_AFSTROOMGEBIED,
    FILENAME_FORCINGS_DISCHARGE,
    FILENAME_FORCINGS_DISCHARGE_META,
    FILENAME_WATERINFO_META_TEMPLATE,
    FILENAME_WATERINFO_TEMPLATE,
    FORCINGS_DISCHARGE_PROCESSED_DIR,
    METADATA_MAP,
    POTENTIAL_EVAPOTRANSPIRATION_LONGNAME,
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
    PRECIPITATION_CATCHMENT_LONGNAME,
    PRECIPITATION_GAUGES_PROVIDERS,
    PRECIPITATION_LONGNAME,
    PRECIPITATION_RAW_DIR,
    STATION_ID_MAARKE_KERKEM,
    STATION_ID_NEDERZWALM,
    STATION_ID_WAREGEM,
    TIMESPACING_DICT,
    VARIABLE_NAME_PRECIPITATION_VMM_CATCHMENT,
    WINDOW_SIZE_CLIMATOLOGY,
)
from loguru import logger


# %% Util functions
def get_complete_years(df: pd.DataFrame):
    start_date = df.index.min()
    end_date = df.index.max()

    first_year = (
        start_date.year
        if start_date.month == 1 and start_date.day == 1
        else start_date.year + 1
    )
    last_year = (
        end_date.year
        if end_date.month == 12 and end_date.day == 31
        else end_date.year - 1
    )

    return start_date, end_date, first_year, last_year


def _read_waterinfo_csv(directory, name: str, station_id: str):
    name_ = name.replace(" ", "_").lower()
    time_spacing = TIMESPACING_DICT["P1D"]
    data_filename = FILENAME_WATERINFO_TEMPLATE.format(
        variable=name_, station_id=station_id, time_spacing=time_spacing
    )
    meta_filename = FILENAME_WATERINFO_META_TEMPLATE.format(
        variable=name_, station_id=station_id, time_spacing=time_spacing
    )
    df = pd.read_csv(directory / data_filename, index_col=0, parse_dates=True)
    df_meta = pd.read_csv(directory / meta_filename)
    return df, df_meta


def custom_thiessen_polygons(
    gdf_gauges: gpd.GeoSeries, gdf_catchment: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Thiessen polygons of the gauges clipped to the catchment, with relative area.

    Based on custom_thiessen_polygons in github.com/olivierbonte/master_thesis.
    """
    box_shape = shapely.box(
        *pd.concat([gdf_gauges, gdf_catchment.geometry]).total_bounds
    )
    if len(gdf_gauges) == 1:
        polygons = [box_shape]
    else:
        voronoi = shapely.ops.voronoi_diagram(
            shapely.MultiPoint(list(gdf_gauges)), envelope=box_shape
        )
        # match polygons to gauges, as voronoi_diagram does not preserve order
        polygons = [
            next(polygon for polygon in voronoi.geoms if polygon.contains(point))
            for point in gdf_gauges
        ]
    gdf_thiessen = gpd.GeoDataFrame(
        {"station_no": gdf_gauges.index}, geometry=polygons, crs=gdf_gauges.crs
    )
    gdf_thiessen_catchment = gdf_thiessen.overlay(
        gdf_catchment[["geometry"]], how="intersection"
    )
    gdf_thiessen_catchment["relative_area"] = (
        gdf_thiessen_catchment.area / gdf_thiessen_catchment.area.sum()
    )
    return gdf_thiessen_catchment.set_index("station_no")


def thiessen_average(
    df_gauges: pd.DataFrame, gdf_gauges: gpd.GeoSeries, gdf_catchment: gpd.GeoDataFrame
) -> pd.Series:
    """Daily Thiessen average, with weights recomputed per set of available gauges."""
    all_gauge_ids = gdf_gauges.index
    # Precompute weights for every combination of gauges, so that a missing gauge's
    # area is redistributed over the remaining gauges (gauges outside catchment get 0)
    weights_per_gauge_set = {}
    for n in range(1, len(gdf_gauges) + 1):
        for gauge_set in combinations(all_gauge_ids, n):
            weights_per_gauge_set[gauge_set] = custom_thiessen_polygons(
                gdf_gauges[list(gauge_set)], gdf_catchment
            )["relative_area"].reindex(gauge_set, fill_value=0.0)

    # Daily weights: group days by which gauges have data, assign that set's weights
    available = df_gauges[all_gauge_ids].notna()
    weights = pd.DataFrame(0.0, index=available.index, columns=all_gauge_ids)

    # Group on all type of combinations of boolean values for the available gauges,
    # and assign the corresponding weights to all days in that group
    days_per_availability_pattern = available.groupby(list(all_gauge_ids)).groups
    for availability_pattern, days in days_per_availability_pattern.items():
        gauge_set = tuple(all_gauge_ids[list(availability_pattern)])
        if gauge_set:
            weights.loc[days, list(gauge_set)] = weights_per_gauge_set[gauge_set].values
    # Missing gauges have weight 0, so filling NaN with 0 does not affect the sum
    precipitation = (df_gauges[all_gauge_ids].fillna(0.0) * weights).sum(axis=1)
    # Days without any gauge data stay NaN instead of 0
    return precipitation.where(available.any(axis=1))


def main():
    FORCINGS_DISCHARGE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Processing meteorological and discharge data")

    # %% Read in data
    logger.info("Reading raw and meta data from CSV files")
    df_dict = {}
    df_meta_dict = {}
    ## Rain gauges, combined into one DataFrame with a column per gauge
    gauge_values, gauge_metas = {}, {}
    for station_id in PRECIPITATION_GAUGES_PROVIDERS:
        df_, df_meta_ = _read_waterinfo_csv(
            PRECIPITATION_RAW_DIR, PRECIPITATION_LONGNAME, station_id
        )
        gauge_values[station_id] = df_["Value"]
        gauge_metas[station_id] = df_meta_
    df_dict[PRECIPITATION_LONGNAME] = pd.DataFrame(gauge_values)
    df_meta_dict[PRECIPITATION_LONGNAME] = pd.concat(
        gauge_metas.values(), ignore_index=True
    )

    ## Other variables
    dict_map_name_to_dir = {
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME: POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
        DISCHARGE_LONGNAME: DISCHARGE_RAW_DIR,
        PRECIPITATION_CATCHMENT_LONGNAME: PRECIPITATION_RAW_DIR,
    }
    dict_map_name_to_station_id = {
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME: STATION_ID_WAREGEM,
        DISCHARGE_LONGNAME: STATION_ID_NEDERZWALM,
        PRECIPITATION_CATCHMENT_LONGNAME: STATION_ID_NEDERZWALM,
    }
    for name, directory in dict_map_name_to_dir.items():
        station_id_ = dict_map_name_to_station_id.get(name)
        if not station_id_:
            logger.warning(f"No station ID found for {name}")
            continue
        df_dict[name], df_meta_dict[name] = _read_waterinfo_csv(
            directory, name, station_id_
        )

    ## Catchment polygon
    gdf_catchment = gpd.read_file(
        CATCHMENT_INFO_PROCESSED_DIR / FILENAME_AFSTROOMGEBIED
    )
    gdf_catchment = gdf_catchment.loc[
        gdf_catchment["A0CODE"] == CATCHMENT_A0CODE
    ].to_crs(EPSG_LAMBERT_72)
    logger.info(
        f"Catchment {CATCHMENT_A0CODE} area: {gdf_catchment.area.sum() / 1e6:.2f} km²"
    )

    # %% Find date ranges and overlapping periods
    logger.info(
        "Finding overlapping periods with full years of data across all variables"
    )

    first_years = []
    last_years = []
    for name, df in df_dict.items():
        start_date, end_date, first_year, last_year = get_complete_years(df)
        logger.info(f"{name} Data - Start: {start_date.date()}, End: {end_date.date()}")
        logger.info(
            f"{name} Data - First complete year: {first_year}, Last complete year: {last_year}"
        )
        first_years.append(first_year)
        last_years.append(last_year)

    start_year = max(first_years)
    end_year = min(last_years)

    if start_year <= end_year:
        logger.info(
            f"Overlapping period with full years of data: {start_year} - {end_year}"
        )
    else:
        msg = "No overlapping period with full years of data across all variables."
        logger.error(msg)
        raise ValueError(msg)

    # %% Filter to overlapping period and fill missing days with NaNs
    # Create daily date range spanning the full, complete years
    logger.info(
        "Filtering data to overlapping period and filling missing days with NaNs"
    )
    date_range = pd.date_range(
        start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="D"
    )

    # Reindex filters existing data to the boundaries of date_range and adds rows for missing days with NaNs
    for name, df in df_dict.items():
        df_ = df.reindex(date_range)
        df_dict[name] = df_

    # %% Precipitation: Thiessen average of rain gauges as additional option
    df_gauges = df_dict[PRECIPITATION_LONGNAME]
    df_meta_gauges = df_meta_dict[PRECIPITATION_LONGNAME]
    gdf_gauges = gpd.GeoSeries(
        gpd.points_from_xy(
            df_meta_gauges["station_local_x"], df_meta_gauges["station_local_y"]
        ),
        index=df_meta_gauges["station_no"],
        crs=EPSG_LAMBERT_72,
    )
    weights_all_gauges = custom_thiessen_polygons(gdf_gauges, gdf_catchment)[
        "relative_area"
    ].reindex(gdf_gauges.index, fill_value=0.0)
    logger.info(
        f"Thiessen weights with all gauges: {weights_all_gauges.round(3).to_dict()}"
    )
    available = df_gauges.notna()
    days_per_gauge_set = available.apply(
        lambda row: ", ".join(row.index[row]) or "none", axis=1
    ).value_counts()
    logger.info(f"Number of days per set of available gauges:\n{days_per_gauge_set}")

    logger.info("Computing daily Thiessen average for each set of available gauges")
    df_dict[PRECIPITATION_LONGNAME] = thiessen_average(
        df_gauges, gdf_gauges, gdf_catchment
    ).to_frame("Value")
    nr_missing_values = df_dict[PRECIPITATION_LONGNAME]["Value"].isna().sum()
    if nr_missing_values > 0:
        msg = f"{nr_missing_values} days without data from any rain gauge."
        logger.error(msg)
        raise ValueError(msg)
    logger.info(f"No missing values in {PRECIPITATION_LONGNAME}")

    # %% Catchment precipitation: gap filling
    logger.info(
        f"Filling missing values in {PRECIPITATION_CATCHMENT_LONGNAME} with station precipitation"
    )
    logger.info(
        f"Number of missing values in {PRECIPITATION_CATCHMENT_LONGNAME} before filling: "
        f"{df_dict[PRECIPITATION_CATCHMENT_LONGNAME]['Value'].isna().sum()}"
    )
    df_dict[PRECIPITATION_CATCHMENT_LONGNAME]["Value"] = df_dict[
        PRECIPITATION_CATCHMENT_LONGNAME
    ]["Value"].fillna(df_gauges[STATION_ID_MAARKE_KERKEM])
    logger.info(
        f"Number of missing values in {PRECIPITATION_CATCHMENT_LONGNAME} after filling: "
        f"{df_dict[PRECIPITATION_CATCHMENT_LONGNAME]['Value'].isna().sum()}"
    )

    # %% Potential evapotranspiration
    ## Remove outliers
    logger.info("Removing outliers from potential evapotranspiration data")
    logger.info(f"Setting values below {EP_MINIMUM} to NaN")
    df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]["Value"] = df_dict[
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME
    ]["Value"].where(
        df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]["Value"] >= EP_MINIMUM
    )
    logger.info(f"Clipping remaining values below {EP_TRESHOLD} to {EP_TRESHOLD}")
    df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]["Value"] = df_dict[
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME
    ]["Value"].clip(lower=EP_TRESHOLD)

    ## Calculate smoothed climatology
    logger.info(
        f"Calculating smoothed climatology for potential evapotranspiration with window size: {WINDOW_SIZE_CLIMATOLOGY}"
    )
    ep_climatology_daily = (
        df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]["Value"]
        .groupby(df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME].index.dayofyear)
        .mean()
    )
    ep_climatology_daily_padded = ep_climatology_daily.to_xarray().pad(
        index=WINDOW_SIZE_CLIMATOLOGY // 2, mode="wrap"
    )
    ep_climatology_daily_smoothed = (
        ep_climatology_daily_padded
        .rolling(
            index=WINDOW_SIZE_CLIMATOLOGY,
            center=True,
            min_periods=WINDOW_SIZE_CLIMATOLOGY,
        )
        .mean()
        .dropna("index")
    ).to_pandas()

    ## Fill missing values with smoothed climatology
    logger.info(
        "Filling missing values in potential evapotranspiration with smoothed climatology"
    )
    logger.info(
        f"Number of missing values in potential evapotranspiration before filling: "
        f"{df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]['Value'].isna().sum()}"
    )
    # Convert the dayofyear Index to a Series so map returns a Series
    doy_series = pd.Series(
        index=df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME].index,
        data=df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME].index.dayofyear,
    )
    # Replace every doy value with the corresponding smoothed climatology value
    ep_climatology_matched = doy_series.map(ep_climatology_daily_smoothed)

    df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]["Value"] = df_dict[
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME
    ]["Value"].fillna(ep_climatology_matched)
    logger.info(
        f"Number of missing values in {POTENTIAL_EVAPOTRANSPIRATION_LONGNAME} after filling: "
        f"{df_dict[POTENTIAL_EVAPOTRANSPIRATION_LONGNAME]['Value'].isna().sum()}"
    )
    # %% Discharge
    nr_negative_values = (df_dict[DISCHARGE_LONGNAME]["Value"] < 0).sum()
    logger.info(
        f"Number of below zero values in {DISCHARGE_LONGNAME}: {nr_negative_values}"
    )
    if nr_negative_values > 0:
        logger.info("Setting below zero values in discharge to zero")
        df_dict[DISCHARGE_LONGNAME]["Value"] = df_dict[DISCHARGE_LONGNAME][
            "Value"
        ].clip(lower=0)
    logger.info(
        f"Number of Nan values in {DISCHARGE_LONGNAME}: {df_dict[DISCHARGE_LONGNAME]['Value'].isna().sum()}. "
        "Nan values are not filled in."
    )

    # %% Combine all variables into a single DataFrame
    out_path_ = FORCINGS_DISCHARGE_PROCESSED_DIR / FILENAME_FORCINGS_DISCHARGE
    logger.info(f"Saving all variables into a single dataset at {out_path_}")
    df_combined = pd.DataFrame(index=date_range)
    for name, df in df_dict.items():
        if name == PRECIPITATION_CATCHMENT_LONGNAME:
            name = VARIABLE_NAME_PRECIPITATION_VMM_CATCHMENT
        name = name.replace(" ", "_").lower()
        df_combined[name] = df["Value"]
    df_combined.to_csv(out_path_)

    # %% Combine and select metadata
    out_path_meta_ = FORCINGS_DISCHARGE_PROCESSED_DIR / FILENAME_FORCINGS_DISCHARGE_META
    logger.info(
        f"Saving, combining and selecting metadata for all variables at {out_path_meta_}"
    )
    metadata_combined = {}
    for name, df_meta in df_meta_dict.items():
        metadata_combined[name] = df_meta[METADATA_MAP.keys()].rename(
            columns=METADATA_MAP
        )
    df_combined_meta = pd.concat(metadata_combined, axis=0).reset_index(
        level=1, drop=True
    )
    df_combined_meta["thiessen_weight"] = (
        df_combined_meta["id"]
        .map(weights_all_gauges)
        .where(df_combined_meta.index == PRECIPITATION_LONGNAME)
    )
    df_combined_meta.to_csv(out_path_meta_)


if __name__ == "__main__":
    main()
