import pandas as pd
from conf import END_YEAR, START_YEAR, STATION_ID_MAARKE_KERKEM, STATION_ID_NEDERZWALM
from pywaterinfo import Waterinfo

vmm = Waterinfo("vmm", cache=True)
station_info_mk = vmm.get_timeseries_list(STATION_ID_MAARKE_KERKEM)
station_info_nz = vmm.get_timeseries_list(STATION_ID_NEDERZWALM)

#
station_info_nz_precip = station_info_nz.query(
    "stationparameter_longname == 'Precipitation of catchment' and ts_name == 'Rro.DagTot'"
)
# date_cols = ["from", "to"]
# for col in date_cols:
#     station_info_nz_precip[col] = pd.to_datetime(station_info_nz_precip[col])

# start_year_nz_precip = station_info_nz_precip["from"].dt.year.values[0] + 1
# end_year_nz_precip = station_info_nz_precip["to"].dt.year.values[0] - 1
ts_id_nz_precip = station_info_nz_precip["ts_id"].values[0]
_start_date = f"{START_YEAR}-01-01"
_end_date = f"{END_YEAR}-01-31"
df_nz_precip = (
    vmm.get_timeseries_values(
        ts_id=ts_id_nz_precip,
        start=_start_date,
        end=_end_date,
    )
    .reset_index()
    .assign(
        Timestamp=lambda df: pd.to_datetime(pd.to_datetime(df["Timestamp"]).dt.date)
    )
    .set_index("Timestamp")
)
