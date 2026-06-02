import openeo
from conf import BBOX, COLLECTION_ID, EPSG_LAMBERT_72
from pyproj import Transformer

connection = openeo.connect(
    "https://openeo.dataspace.copernicus.eu"
).authenticate_oidc()
collection_description = connection.describe_collection(COLLECTION_ID)

bands = collection_description["cube:dimensions"]["bands"]["values"]

start_date = collection_description["extent"]["temporal"]["interval"][0][0].split("T")[
    0
]
# end_date = collection_description["extent"]["temporal"]["interval"][0][1]
end_date = (
    str(int(start_date[:4]) + 1) + start_date[4:]
)  # add one year to the start datetemporal_extent = [start_date, end_date]
temporal_extent = [start_date, end_date]

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
ssm_cube = connection.load_collection(
    COLLECTION_ID,
    spatial_extent=spatial_extent,
    temporal_extent=temporal_extent,
    bands=bands,
)
job = ssm_cube.execute_batch("satellite_soil_moisture.nc", out_format="NetCDF")
job.start_and_wait()
job.get_results().download_files(".")
