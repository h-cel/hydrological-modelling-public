import datetime
import time

import openeo
import pandas as pd
from conf import (
    BBOX,
    COLLECTION_ID,
    EPSG_LAMBERT_72,
    SATELLITE_SOIL_MOISTURE_RAW_DIR,
    logger,
)
from pyproj import Transformer


def main():
    SATELLITE_SOIL_MOISTURE_RAW_DIR.mkdir(parents=True, exist_ok=True)

    connection = openeo.connect(
        "https://openeo.dataspace.copernicus.eu"
    ).authenticate_oidc()

    logger.info(f"Fetching collection description for {COLLECTION_ID}")
    collection_description = connection.describe_collection(COLLECTION_ID)

    bands = collection_description["cube:dimensions"]["bands"]["values"]
    logger.info(f"Detected bands: {bands}")

    start_date = collection_description["extent"]["temporal"]["interval"][0][0].split(
        "T"
    )[0]

    raw_end = collection_description["extent"]["temporal"]["interval"][0][1]
    if raw_end is None:
        # Collection has no declared end date; use the last day of the previous year
        end_date = f"{datetime.datetime.now(tz=datetime.UTC).date().year - 1}-12-31"
        logger.info(
            f"Collection end date is None; defaulting to last day of previous year: {end_date}"
        )
    else:
        end_date = raw_end.split("T")[0]

    logger.info(f"Temporal coverage: {start_date} → {end_date}")

    transformer = Transformer.from_crs(
        f"EPSG:{EPSG_LAMBERT_72}", "EPSG:4326", always_xy=True
    )
    bbox_bd72 = BBOX  # in m (EPSG:31370)
    bbox_wgs84 = transformer.transform_bounds(*bbox_bd72)  # in degrees (EPSG:4326)
    spatial_extent = {
        "west": bbox_wgs84[0],
        "south": bbox_wgs84[1],
        "east": bbox_wgs84[2],
        "north": bbox_wgs84[3],
    }

    # Load the full collection without a temporal filter; we will slice per year below
    ssm_cube = connection.load_collection(
        COLLECTION_ID,
        spatial_extent=spatial_extent,
        bands=bands,
    )

    start_year = int(start_date[:4])
    end_year = int(end_date[:4])

    job_dict = {}
    for year in range(start_year, end_year + 1):
        year_start = max(start_date, f"{year}-01-01")
        # Use {year+1}-01-01 as the exclusive upper bound instead of {year}-12-31,
        # because OpenEO's filter_temporal uses a half-open interval [start, end),
        # which would otherwise exclude all data on Dec 31.
        year_end = min(f"{end_year + 1}-01-01", f"{year + 1}-01-01")

        logger.info(
            f"Creating job for year {year} ({year_start} → {year_end}, exclusive)"
        )
        year_cube = ssm_cube.filter_temporal(year_start, year_end)
        job = year_cube.create_job(out_format="NetCDF", title=f"SSM {year}")
        job_dict[year] = job.job_id
        job.start()
        logger.info(f"Job for {year} started with ID {job.job_id}")

    # Save job IDs to a text file for reference
    job_ids_file = SATELLITE_SOIL_MOISTURE_RAW_DIR / "job_ids.csv"
    df_job_ids = pd.DataFrame.from_dict(job_dict, orient="index", columns=["job_id"])
    df_job_ids.to_csv(job_ids_file)

    # Allow to read back job_ids from the file in case you need to rerun the script
    df_job_ids = pd.read_csv(job_ids_file, index_col=0)

    for year, job_id in job_dict.items():
        job = connection.job(job_id)
        while job.status() != "finished":
            logger.info(f"Waiting for job {job_id} (year {year}) to finish...")
            time.sleep(30)  # Wait for 30 seconds before checking again
        logger.info(f"Job for {year} completed, downloading results...")
        folder_ = SATELLITE_SOIL_MOISTURE_RAW_DIR / f"{year}"
        folder_.mkdir(parents=True, exist_ok=True)
        job.get_results().download_files(folder_)
        logger.info(f"Year {year} downloaded to {folder_}")


if __name__ == "__main__":
    main()
