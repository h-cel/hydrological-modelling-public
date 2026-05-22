import os
from pathlib import Path

import numpy as np
import rioxarray
from conf import DATASET_DTM, dtm_raw_dir
from owslib.wcs import WebCoverageService
from rioxarray.merge import merge_arrays

dtm_raw_dir.mkdir(parents=True, exist_ok=True)

# Full metadata at https://metadata.vlaanderen.be/srv/dut/catalog.search#/metadata/f52b1a13-86bc-4b64-8256-88cc0d1a8735
wcs_url = "https://geo.api.vlaanderen.be/DHMV/wcs"
wcs = WebCoverageService(wcs_url, version="2.0.1")
CRS = "http://www.opengis.net/def/crs/EPSG/0/31370"
FORMAT = wcs.contents[DATASET_DTM].supportedFormats[-1]
NO_DATA_VALUE = -9999.0
output_file = dtm_raw_dir / f"{DATASET_DTM}.tif"

# Target extent
global_minx, global_maxx = 98_000, 116_000
global_miny, global_maxy = 160_000, 180_000

# Note: extent too large for a single request, so we split it into tiles and merge later
step = 2_000  # m
x_edges = np.arange(global_minx, global_maxx + step, step)
y_edges = np.arange(global_miny, global_maxy + step, step)
tile_files = []


# Define function to download a subset of the coverage using WCS GetCoverage request
def download_wcs_subset(
    wcs: WebCoverageService,
    minx: float,
    maxx: float,
    miny: float,
    maxy: float,
    out_file: Path,
):
    print(f"Downloading subset {minx:.1f}-{maxx:.1f}, {miny:.1f}-{maxy:.1f}...")
    try:
        response = wcs.getCoverage(
            identifier=DATASET_DTM,
            crs=CRS,
            format=FORMAT,
            subsets=[("x", minx, maxx), ("y", miny, maxy)],
        )

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
        print(f"Failed to download subset: {e}")
        return False


print("Starting DTM download in tiles")
for i in range(len(x_edges) - 1):
    for j in range(len(y_edges) - 1):
        xmin, xmax = x_edges[i].item(), x_edges[i + 1].item()
        ymin, ymax = y_edges[j].item(), y_edges[j + 1].item()

        tile_file = dtm_raw_dir / f"tile_{i}_{j}.tif"
        download_wcs_subset(wcs, xmin, xmax, ymin, ymax, tile_file)
        tile_files.append(tile_file)

print(f"Downloaded {len(tile_files)} tiles. Merging into single DTM")

elements = []
for f in tile_files:
    try:
        da = rioxarray.open_rasterio(f)
        elements.append(da)
    except Exception as e:
        print(f"Could not open {f}: {e}")

if elements:
    da_merged = merge_arrays(elements, nodata=NO_DATA_VALUE)
    da_merged.rio.to_raster(output_file)
    print(f"Successfully merged DTM tiles into: {output_file}")
    da_merged.close()

    # Test if opening the merged file works
    ds = rioxarray.open_rasterio(output_file)
    print(ds)
else:
    print("No valid tiles to merge.")

# Cleanup tile files
for f in tile_files:
    os.remove(f)
