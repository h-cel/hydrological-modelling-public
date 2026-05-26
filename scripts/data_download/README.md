# Data downloads

Below some extra information on the downloaded datasets. Note that all configuration settings for the download (path names, variables...) are grouped in [`conf.py`](conf.py). 

## Digital Terrain Model (DTM)

Download file: [`dtm_download.py`](dtm_download.py)

The DTM used is *Digitaal Hoogtemodel Vlaanderen II, DTM, raster, 1 m*. For the full metadata, see [here](https://metadata.vlaanderen.be/srv/api/records/f52b1a13-86bc-4b64-8256-88cc0d1a8735?language=dut). The coordinate reference system is [Belgian Lambert 72](https://www.opengis.net/def/crs/EPSG/0/31370). Data is only requested via [OWSLib](https://github.com/geopython/OWSLib) for the region around the Zwalm catchment using the [WebCoverageService (WCS) provided by the Flemish Government](https://www.vlaanderen.be/datavindplaats/catalogus/wcs-digitaal-hoogtemodel-vlaanderen). Alternatively, one could (as of 22/05/2026) also download this dataset manually via [this url](https://download.vlaanderen.be/product/939-digitaal-hoogtemodel-vlaanderen-ii-dtm-raster-1-m). 


## Waterinfo

Download file: [`waterinfo_download.py`](waterinfo_download.py)

[Waterinfo](https://www.waterinfo.vlaanderen.be/) is primary Flemish source of hydrological data. For this exercise, all data is at a daily temporal resolution. Programmatic access is carried out using [pywaterinfo](https://github.com/fluves/pywaterinfo). Following variables are downloaded:

- Discharge: Daily average discharge [$`\text{m}^3`$/s] measured at Nederzwalm/Zwalmbeek (L06_342)
- Precipitation: Daily total precipitation [mm] 
    - Catchment rainfall (merging radar + pluviograph) for L06_342
    - Pluviograph rainfall from Maarke-Kerkem (P06_014)
- Potential evapotranspiration: Daily total potential evapotranspiration [mm] calculated with the Penman method at the meteorological station in Waregem (ME05_019)

## Vlaamse Hydrografische Atlas (VHA)

Download file: [`vha_download.py`](vha_download.py)

The [Vlaamse Hydrografische Atlas](https://metadata.vlaanderen.be/srv/api/records/d5a7a3df-a8a5-4516-92c4-d0128eea7fd7?language=dut) contains the current trajectories of all waterways in Flanders. The vector data is requested via [OWSLib](https://github.com/geopython/OWSLib) for the same Zwalm region as the DTM, using the [Web Feature Service (WFS) provided by the Flemish Government](https://www.vlaanderen.be/datavindplaats/catalogus/wfs-vlaamse-hydrografische-atlas-waterlopen). Alternatively, one could (as of 26/05/2026), download the dataset manually via [this url](https://www.vlaanderen.be/datavindplaats/catalogus/vlaamse-hydrografische-atlas-waterlopen-toestand-03-02-2026). 

## Afstroomgebied

Download file: [`afstroomgebied_download.py`](afstroomgebied_download.py)

The [Oppervlaktewaterlichamen en hun afstroomgebieden (2022-2027)](https://metadata.vlaanderen.be/srv/api/records/e8f55350-5c8d-4b15-ac09-1014469c3f04?language=dut) dataset contains all surface water bodies and catchment areas for Flanders. The vector data is requested via [OWSLib](), once more for the same Zwalm region as the DTM, using the [Web Feature Service (WFS) provided by the Flemish Government](https://www.vlaanderen.be/datavindplaats/catalogus/wfs-oppervlaktewaterlichamen). Alternatively, one could (as of 26/05/2026), download the dataset manually via [this url](https://www.vlaanderen.be/datavindplaats/catalogus/oppervlaktewaterlichamen-en-hun-afstroomgebieden-2022-2027). Here, only catchment areas of type A0 are retrieved. Every surface water body is associated with a corresponding catchment area. The convention for denoting the aggregation of these areas by the Flemish government is (based on [the release notes](https://www.vlaanderen.be/digitaal-vlaanderen/nieuws-0/release-oppervlaktewaterlichamen-en-hun-afstroomgebieden-2022-2027)): A2 (smallest) &rarr; A1 &rarr; A0 &rarr; *Bekken* &rarr; *Stroomgebieddistrict* (largest)