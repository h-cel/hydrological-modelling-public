from catchment_info_process import main as process_catchment_info
from conf import LOG_FORMAT, PROCESSED_DATA_DIR, logger
from dtm_process import main as process_dtm
from forcings_discharge_process import main as process_forcings_discharge
from satellite_soil_moisture_process import main as process_satellite_soil_moisture

logger.info("Starting data process")

if __name__ == "__main__":
    log_file = PROCESSED_DATA_DIR / "data_process_{time}.log"
    logger.add(log_file, format=LOG_FORMAT, enqueue=True, mode="w")

    logger.info("Running catchment_info_process.py...")
    process_catchment_info()

    logger.info("Running dtm_process.py...")
    process_dtm()

    logger.info("Running forcings_discharge_process.py...")
    process_forcings_discharge()

    logger.info("Running satellite_soil_moisture_process.py...")
    process_satellite_soil_moisture()
