# %% Imports
import pandas as pd
from conf import (
    DISCHARGE_RAW_DIR,
    EP_MINIMUM,
    EP_TRESHOLD,
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR,
    PRECIPITATION_RAW_DIR,
    STATION_ID_MAARKE_KERKEM,
    STATION_ID_NEDERZWALM,
    STATION_ID_WAREGEM,
)


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


# %% Read in data
df_nz_p = pd.read_csv(
    PRECIPITATION_RAW_DIR
    / f"precipitation_of_catchment_{STATION_ID_NEDERZWALM}_daily.csv",
    index_col=0,
    parse_dates=True,
)
df_mk_p = pd.read_csv(
    PRECIPITATION_RAW_DIR / f"precipitation_{STATION_ID_MAARKE_KERKEM}_daily.csv",
    index_col=0,
    parse_dates=True,
)
df_wa_ep = pd.read_csv(
    POTENTIAL_EVAPOTRANSPIRATION_RAW_DIR
    / f"potential_evapotranspiration_{STATION_ID_WAREGEM}_daily.csv",
    index_col=0,
    parse_dates=True,
)
df_nz_discharge = pd.read_csv(
    DISCHARGE_RAW_DIR / f"discharge_{STATION_ID_NEDERZWALM}_daily.csv",
    index_col=0,
    parse_dates=True,
)


# %% Find date ranges and overlapping periods
df_dict = {
    "Precipitation": df_nz_p,
    "Catchment Precipitation": df_mk_p,
    "Potential Evapotranspiration": df_wa_ep,
    "Discharge": df_nz_discharge,
}

first_years = []
last_years = []
for name, df in df_dict.items():
    start_date, end_date, first_year, last_year = get_complete_years(df)
    print(f"  Start: {start_date.date()}, End: {end_date.date()}")
    print(f"  First complete year: {first_year}, Last complete year: {last_year}")
    first_years.append(first_year)
    last_years.append(last_year)

start_year = max(first_years)
end_year = min(last_years)

if start_year <= end_year:
    print(f"Overlapping period with full years of data: {start_year} - {end_year}")
else:
    raise ValueError("No overlapping period with full years of data.")

# %% Filter to overlapping period and fill missing days
# Create daily date range spanning the full, complete years
date_range = pd.date_range(
    start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="D"
)

# Reindex filters existing data to the boundaries of date_range and adds rows for missing days with NaNs
for name, df in df_dict.items():
    df_ = df.reindex(date_range)
    df_dict[name] = df_

# %% Precipitation: gap fill missing values in catchment precipitation with station precipitation
df_dict["Catchment Precipitation"] = df_dict["Catchment Precipitation"].fillna(
    df_dict["Precipitation"]
)

# %% Potential evpotranspiration
## Remove outliers
df_dict["Potential Evapotranspiration"]["Value"] = df_dict[
    "Potential Evapotranspiration"
]["Value"].where(df_dict["Potential Evapotranspiration"]["Value"] >= EP_MINIMUM)
df_dict["Potential Evapotranspiration"]["Value"] = df_dict[
    "Potential Evapotranspiration"
]["Value"].clip(lower=EP_TRESHOLD)

## Calculate smoothed climatology
HALF_WINDOW_SIZE = 5
WINDOW_SIZE = 2 * HALF_WINDOW_SIZE + 1

ep_climatology_daily = (
    df_dict["Potential Evapotranspiration"]["Value"]
    .groupby(df_dict["Potential Evapotranspiration"].index.dayofyear)
    .mean()
)
ep_climatology_daily_padded = ep_climatology_daily.to_xarray().pad(
    index=WINDOW_SIZE // 2, mode="wrap"
)
ep_climatology_daily_smoothed = (
    ep_climatology_daily_padded.rolling(
        index=WINDOW_SIZE, center=True, min_periods=WINDOW_SIZE
    )
    .mean()
    .dropna("index")
).to_pandas()

## Fill missing values with smoothed climatology
# Convert the dayofyear Index to a Series so map returns a Series
doy_series = pd.Series(
    data=df_dict["Potential Evapotranspiration"].index.dayofyear,
    index=df_dict["Potential Evapotranspiration"].index,
)
# Replace every doy value with the corresponding smoothed climatology value
ep_climatology_matched = doy_series.map(ep_climatology_daily_smoothed)

df_dict["Potential Evapotranspiration"]["Value"] = df_dict[
    "Potential Evapotranspiration"
]["Value"].fillna(ep_climatology_matched)
# %%
