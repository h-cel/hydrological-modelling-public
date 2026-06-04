# Data processing

Below some extra information on how the downloaded datasets (see [data downloads](../data_download/README.md)) are processed. Configuration settings are again given in [`conf.py`](conf.py). All processed data is grouped in `data/processed`. To execute all the processing tasks at once, run [`main_process.py`](main_process.py).

## Catchment information

Processing file: [`catchment_info_process.py`](catchment_info_process.py)

Both to the river network of the *Vlaamse Hydrografische Atlas* as the downloaded catchment area, no further processing is applied out. There is only a check to make sure that the area of interest is contained in the downloaded datasets. 

## Digital terrain model (DTM)

Processing file: [`dtm_process.py`](dtm_process.py)

Because working with the DTM at its native spatial resolution (1m) would be very computationally expensive, the DTM is resampled to a coarser spatial resolution of 10m by a simple averaging. 

## Forcings and discharge

Processing file: [`forcings_and_discharge_process.py`](forcings_and_discharge_process.py)

First, a common period of full years over all 3 variables (precipitation, potential evapotranspiration and discharge) is determined. 

For precipitation, the catchment rainfall is preferred over the pluviograph rainfall. When no catchment rainfall is available for a given time step, the pluviograph rainfall is used instead. The potential evapotranspiration is gapfilled using a smoothed climatology. For discharge, no gapfilling is applied, only values below zero are set to zero. 

## Satellite soil moisture

Processing file: [`satellite_soil_moisture_process.py`](satellite_soil_moisture_process.py)
