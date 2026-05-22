import rootutils

# General paths
root_path = rootutils.find_root(search_from=__file__, indicator=".git")
data_dir = root_path / "data"
raw_data_dir = data_dir / "raw"
processed_data_dir = data_dir / "processed"

# DTM info
DATASET_DTM = "DHMVII_DTM_1m"  # DHMVI_DTM_5m (outdated)
dtm_raw_dir = raw_data_dir / "DTM"
dtm_processed_dir = processed_data_dir / "DTM"
DTM_SPATIAL_RESOLUTION = 1.0  # in meters
DTM_SPATIAL_RESOLUTION_UPSCALED = 10.0  # in meters
