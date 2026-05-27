import os
from pathlib import Path

import numpy as np
import rioxarray
from conf import (
    CRS,
    DATASET_DTM,
    DTM_RAW_DIR,
    FILENAME_DTM,
    NO_DATA_VALUE_DTM,
    TILE_SIZE,
    WCS_ENDPOINT_DTM,
    XMAX,
    XMIN,
    YMAX,
    YMIN,
    logger,
)
from owslib.wcs import WebCoverageService
from rioxarray.merge import merge_arrays


# Define function to download a subset of the coverage using WCS GetCoverage request
def download_wcs_subset(
    wcs: WebCoverageService,
    minx: float,
    maxx: float,
    miny: float,
    maxy: float,
    out_file: Path,
):
    logger.info(f"Downloading subset {minx:.1f}-{maxx:.1f}, {miny:.1f}-{maxy:.1f}...")
    try:
        response = wcs.getCoverage(
            identifier=DATASET_DTM,
            crs=CRS,
            format=FORMAT,
            subsets=[("x", minx, maxx), ("y", miny, maxy)],
        )

        # Response contains both metadata and the image -> response processing needed
        # Following https://stackoverflow.com/questions/77838318/get-image-from-multipart-response-from-a-web-coverage-service-wcs-using-python
        data = response.read()
        boundary = b"--wcs"
        image_tif = data
        if boundary in data and b"Content-Type: image/tiff" in data:
            for part in data.split(boundary):
                if b"Content-Type: image/tiff" in part:
                    if b"II*" in part:
                        index = part.index(b"II*")
                        image_tif = part[index:]
                    break

        with open(out_file, "wb") as f:
            f.write(image_tif)

        return True
    except Exception as e:
        logger.error(f"Failed to download subset: {e}")
        return False


def main():
    DTM_RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Full metadata at https://metadata.vlaanderen.be/srv/dut/catalog.search#/metadata/f52b1a13-86bc-4b64-8256-88cc0d1a8735
    logger.info(f"Downloading {DATASET_DTM} via WCS from {WCS_ENDPOINT_DTM}")
    wcs = WebCoverageService(WCS_ENDPOINT_DTM, version="2.0.1")
    global FORMAT
    FORMAT = wcs.contents[DATASET_DTM].supportedFormats[-1]
    output_path = DTM_RAW_DIR / FILENAME_DTM

    # Note: extent too large for a single request, so we split it into tiles and merge later
    tile_files = []
    x_edges = np.arange(XMIN, XMAX + TILE_SIZE, TILE_SIZE)
    y_edges = np.arange(YMIN, YMAX + TILE_SIZE, TILE_SIZE)

    logger.info("Starting DTM download in tiles")
    for i in range(len(x_edges) - 1):
        for j in range(len(y_edges) - 1):
            xmin, xmax = x_edges[i].item(), x_edges[i + 1].item()
            ymin, ymax = y_edges[j].item(), y_edges[j + 1].item()

            tile_file = DTM_RAW_DIR / f"tile_{i}_{j}.tif"
            download_wcs_subset(wcs, xmin, xmax, ymin, ymax, tile_file)
            tile_files.append(tile_file)

    logger.info(f"Downloaded {len(tile_files)} tiles. Merging into single DTM")

    elements = []
    for f in tile_files:
        try:
            da = rioxarray.open_rasterio(f)
            elements.append(da)
        except Exception as e:
            logger.error(f"Could not open {f}: {e}")

    if elements:
        da_merged = merge_arrays(elements, nodata=NO_DATA_VALUE_DTM)
        da_merged.rio.to_raster(output_path)
        logger.info(f"Successfully merged DTM tiles into: {output_path}")
        da_merged.close()

        # Close all individual opened files to prevent sys.excepthook errors on exit
        for da in elements:
            da.close()
    else:
        logger.warning("No valid tiles to merge.")

    # Cleanup tile files
    for f in tile_files:
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    main()
