# %% Imports
import pandas as pd
from conf import (
    DAILY_AGG,
    DISCHARGE_LONGNAME,
    DISCHARGE_RAW_DIR,
    FILENAME_WATERINFO_META_TEMPLATE,
    FILENAME_WATERINFO_TEMPLATE,
    MEAN_AGG,
    POTENTIAL_EVAPOTRANSPIRATION_LONGNAME,
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
    POTENTIAL_EVAPOTRANSPIRATION_SUFFIX,
    PRECIPITATION_CATCHMENT_LONGNAME,
    PRECIPITATION_CATCHMENT_SUFFIX,
    PRECIPITATION_LONGNAME,
    PRECIPITATION_RAW_DIR,
    STATION_ID_MAARKE_KERKEM,
    STATION_ID_NEDERZWALM,
    STATION_ID_WAREGEM,
    TIMESPACING_DICT,
    TOTAL_AGG,
    logger,
)
from pywaterinfo import Waterinfo


# %% Helper functions
def _parse_date_columns(
    df: pd.DataFrame, date_cols: list = ["from", "to"]
) -> pd.DataFrame:
    """Parse specified date columns in a DataFrame into pandas datetime objects."""
    df = df.copy()
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def _download_daily_timeseries(vmm, station_info: pd.DataFrame) -> pd.DataFrame:
    """Download full daily timeseries for a filtered station_info DataFrame with exactly 1 entry."""
    if len(station_info) != 1:
        raise ValueError(
            f"Expected exactly 1 entry in station_info, got {len(station_info)}."
        )
    ts_id = station_info["ts_id"].values[0]
    return (
        vmm
        .get_timeseries_values(
            ts_id=ts_id,
            start=station_info["from"].dt.date.values[0],
            end=station_info["to"].dt.date.values[0],
        )
        .reset_index()
        .assign(
            Timestamp=lambda df: pd.to_datetime(pd.to_datetime(df["Timestamp"]).dt.date)
        )
        .set_index("Timestamp")
    )


def _write_timeseries(
    df: pd.DataFrame,
    station_info: pd.DataFrame,
    output_dir,
    variable_longname: str,
    station_id: str,
) -> None:
    """Write timeseries data and its metadata to CSV files in output_dir."""
    time_spacing = TIMESPACING_DICT[station_info["ts_spacing"].values[0]]
    variable_longname = variable_longname.replace(" ", "_").lower()

    data_filename = FILENAME_WATERINFO_TEMPLATE.format(
        variable=variable_longname, station_id=station_id, time_spacing=time_spacing
    )
    meta_filename = FILENAME_WATERINFO_META_TEMPLATE.format(
        variable=variable_longname, station_id=station_id, time_spacing=time_spacing
    )

    data_path = output_dir / data_filename
    meta_path = output_dir / meta_filename

    df.to_csv(data_path)
    logger.info(f"Timeseries data saved to {data_path}")

    station_info.to_csv(meta_path, index=False)
    logger.info(f"Timeseries metadata saved to {meta_path}")


def main():
    PRECIPITATION_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DISCHARGE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR.mkdir(parents=True, exist_ok=True)
    vmm = Waterinfo("vmm", cache=True)

    logger.info("Starting downloads from pywaterinfo")
    # %% Nederzwalm/Zwalmbeek (L06_342)
    station_info_nz = _parse_date_columns(
        vmm.get_timeseries_list(STATION_ID_NEDERZWALM)
    )

    ## Catchment precipitation
    logger.info(
        f"Downloading {PRECIPITATION_CATCHMENT_LONGNAME} for station {STATION_ID_NEDERZWALM}"
    )
    station_info_nz_precip = station_info_nz.query(
        f"stationparameter_longname == '{PRECIPITATION_CATCHMENT_LONGNAME}'"
        f" and ts_shortname == '{DAILY_AGG}.{TOTAL_AGG}.{PRECIPITATION_CATCHMENT_SUFFIX}'"
    )
    df_nz_precip = _download_daily_timeseries(vmm, station_info_nz_precip)
    _write_timeseries(
        df_nz_precip,
        station_info_nz_precip,
        PRECIPITATION_RAW_DIR,
        PRECIPITATION_CATCHMENT_LONGNAME,
        STATION_ID_NEDERZWALM,
    )

    ## Discharge
    logger.info(f"Downloading {DISCHARGE_LONGNAME} for station {STATION_ID_NEDERZWALM}")
    station_info_nz_discharge = station_info_nz.query(
        f"stationparameter_longname == '{DISCHARGE_LONGNAME}'"
        f" and ts_shortname == '{DAILY_AGG}.{MEAN_AGG}'"
    )
    df_nz_discharge = _download_daily_timeseries(vmm, station_info_nz_discharge)
    _write_timeseries(
        df_nz_discharge,
        station_info_nz_discharge,
        DISCHARGE_RAW_DIR,
        DISCHARGE_LONGNAME,
        STATION_ID_NEDERZWALM,
    )

    # %% Maarke-Kerkem (P06_014)
    logger.info(
        f"Downloading {PRECIPITATION_LONGNAME} for station {STATION_ID_MAARKE_KERKEM}"
    )
    station_info_mk = _parse_date_columns(
        vmm.get_timeseries_list(STATION_ID_MAARKE_KERKEM)
    )
    station_info_mk_precip = station_info_mk.query(
        f"stationparameter_longname == '{PRECIPITATION_LONGNAME}'"
        f" and ts_shortname == '{DAILY_AGG}.{TOTAL_AGG}'"
    )
    df_mk_precip = _download_daily_timeseries(vmm, station_info_mk_precip)
    _write_timeseries(
        df_mk_precip,
        station_info_mk_precip,
        PRECIPITATION_RAW_DIR,
        PRECIPITATION_LONGNAME,
        STATION_ID_MAARKE_KERKEM,
    )

    # %% Waregem (ME05_019)
    logger.info(
        f"Downloading {POTENTIAL_EVAPOTRANSPIRATION_LONGNAME} for station {STATION_ID_WAREGEM}"
    )
    station_info_waregem = _parse_date_columns(
        vmm.get_timeseries_list(STATION_ID_WAREGEM)
    )
    station_info_waregem_potential_evapotranspiration = station_info_waregem.query(
        f"stationparameter_longname == '{POTENTIAL_EVAPOTRANSPIRATION_LONGNAME}'"
        f" and ts_shortname == '{DAILY_AGG}.{TOTAL_AGG}.{POTENTIAL_EVAPOTRANSPIRATION_SUFFIX}'"
    )
    df_waregem_pet = _download_daily_timeseries(
        vmm, station_info_waregem_potential_evapotranspiration
    )
    _write_timeseries(
        df_waregem_pet,
        station_info_waregem_potential_evapotranspiration,
        POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
        POTENTIAL_EVAPOTRANSPIRATION_LONGNAME,
        STATION_ID_WAREGEM,
    )


if __name__ == "__main__":
    main()
