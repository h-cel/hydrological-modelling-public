# %% Imports
import pandas as pd
from conf import (
    DISCHARGE_LONGNAME,
    DISCHARGE_RAW_DIR,
    EP_MINIMUM,
    EP_TRESHOLD,
    FILENAME_FORCINGS_DISCHARGE,
    FILENAME_FORCINGS_DISCHARGE_META,
    FILENAME_WATERINFO_META_TEMPLATE,
    FILENAME_WATERINFO_TEMPLATE,
    FORCINGS_DISCHARGE_PROCESSED_DIR,
    METADATA_MAP,
    POTENTIAL_EVAPOTRANSPIRATION_LONGNAME,
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
    PRECIPITATION_CATCHMENT_LONGNAME,
    PRECIPITATION_LONGNAME,
    PRECIPITATION_RAW_DIR,
    STATION_ID_MAARKE_KERKEM,
    STATION_ID_NEDERZWALM,
    STATION_ID_WAREGEM,
    TIMESPACING_DICT,
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


def main():
    FORCINGS_DISCHARGE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Processing meteorological and discharge data")

    # %% Read in data
    logger.info("Reading raw and meta data from CSV files")
    df_dict = {}
    df_meta_dict = {}
    dict_map_name_to_dir = {
        PRECIPITATION_LONGNAME: PRECIPITATION_RAW_DIR,
        PRECIPITATION_CATCHMENT_LONGNAME: PRECIPITATION_RAW_DIR,
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME: POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
        DISCHARGE_LONGNAME: DISCHARGE_RAW_DIR,
    }
    dict_map_name_to_station_id = {
        PRECIPITATION_LONGNAME: STATION_ID_MAARKE_KERKEM,
        PRECIPITATION_CATCHMENT_LONGNAME: STATION_ID_NEDERZWALM,
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME: STATION_ID_WAREGEM,
        DISCHARGE_LONGNAME: STATION_ID_NEDERZWALM,
    }
    for name, directory in dict_map_name_to_dir.items():
        station_id_ = dict_map_name_to_station_id.get(name)
        if not station_id_:
            logger.warning(f"No station ID found for {name}")
            continue

        name_ = name.replace(" ", "_").lower()
        time_spacing = TIMESPACING_DICT["P1D"]

        data_filename = FILENAME_WATERINFO_TEMPLATE.format(
            variable=name_, station_id=station_id_, time_spacing=time_spacing
        )
        meta_filename = FILENAME_WATERINFO_META_TEMPLATE.format(
            variable=name_, station_id=station_id_, time_spacing=time_spacing
        )

        df_ = pd.read_csv(
            directory / data_filename,
            index_col=0,
            parse_dates=True,
        )
        df_meta_ = pd.read_csv(directory / meta_filename)
        df_dict[name] = df_
        df_meta_dict[name] = df_meta_

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

    # %% Precipitation: gap fill missing values in catchment precipitation with station precipitation
    logger.info(
        f"Filling missing values in {PRECIPITATION_CATCHMENT_LONGNAME} with station precipitation"
    )
    logger.info(
        f"Number of missing values in {PRECIPITATION_CATCHMENT_LONGNAME} before filling: "
        f"{df_dict[PRECIPITATION_CATCHMENT_LONGNAME]['Value'].isna().sum()}"
    )
    df_dict[PRECIPITATION_CATCHMENT_LONGNAME] = df_dict[
        PRECIPITATION_CATCHMENT_LONGNAME
    ].fillna(df_dict[PRECIPITATION_LONGNAME])
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
        if (
            name != PRECIPITATION_CATCHMENT_LONGNAME
        ):  # avoid duplicate info with station precipitation
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
    df_combined_meta.to_csv(out_path_meta_)


if __name__ == "__main__":
    main()
