# Generates the geospatial figures shown in 0_study_area_and_data.qmd, so that
# rendering the report does not require the geospatial stack (see environment_dev.yml).
# %% Imports
import contextily as cx
import geodatasets as gds
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rioxarray  # noqa: F401
import xarray as xr
from conf import (
    CATCHMENT_INFO_PROCESSED_DIR,
    FIGURES_STUDY_AREA_DIR,
    FILENAME_FIG_SSM_ORIGINAL,
    FILENAME_FIG_WATERINFO_SITES,
    FILENAME_FIG_ZWALMBEEK,
    FILENAME_FORCINGS_DISCHARGE_META,
    FILENAME_VHA,
    FORCINGS_DISCHARGE_PROCESSED_DIR,
    ROOT_PATH,
    SATELLITE_SOIL_MOISTURE_PROCESSED_DIR,
    VARIABLE_NAME_SATELLITE_SOIL_MOISTURE,
)
from loguru import logger
from shapely.geometry import box

# %% Constants
MAP_SOURCE = cx.providers.Esri.WorldStreetMap
ATTRIBUTION_TEXT_SIZE = 1
DPI = 300


# %% Functions
def save(fig, filename):
    output_file = FIGURES_STUDY_AREA_DIR / filename
    fig.savefig(output_file, dpi=DPI)
    plt.close(fig)
    logger.info(f"Figure saved to: {output_file}")


def plot_zwalmbeek(gdf_zwalmbeek):
    # Following https://geopandas.org/en/stable/gallery/plotting_basemap_background.html
    fig, ax = plt.subplots(figsize=(4, 4), constrained_layout=True)
    gdf_zwalmbeek.plot(ax=ax)
    cx.add_basemap(
        ax,
        source=MAP_SOURCE,
        crs=gdf_zwalmbeek.crs,
        zoom=12,
        attribution_size=ATTRIBUTION_TEXT_SIZE,
    )
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.ticklabel_format(useMathText=True, scilimits=(0, 0))

    # Inset axis to show the location within Belgium
    # Following https://geopandas.org/en/latest/gallery/inset_map.html
    iax = ax.inset_axes([0.05, 0.5, 0.4, 0.4], xticks=[], yticks=[])
    europe = gpd.read_file(gds.get_url("eurostat.nuts_rg_10m_2024_3035"))
    country_level = 0  # only keep country level, not regions
    country_code_belgium = "BE"
    belgium = europe[
        (europe.CNTR_CODE == country_code_belgium) & (europe.LEVL_CODE == country_level)
    ].to_crs(gdf_zwalmbeek.crs)
    belgium.plot(ax=iax, color="whitesmoke", edgecolor="black")
    minx, miny, maxx, maxy = gdf_zwalmbeek.total_bounds
    bbox_zwalm = gpd.GeoSeries([box(minx, miny, maxx, maxy)], crs=gdf_zwalmbeek.crs)
    bbox_zwalm.plot(ax=iax, color="none", edgecolor="red", linewidth=1.5)
    save(fig, FILENAME_FIG_ZWALMBEEK)


def plot_waterinfo_sites(gdf_zwalmbeek):
    df_meta = pd.read_csv(
        FORCINGS_DISCHARGE_PROCESSED_DIR / FILENAME_FORCINGS_DISCHARGE_META,
        index_col=0,
    )
    gdf_meta = gpd.GeoDataFrame(
        df_meta,
        geometry=gpd.points_from_xy(df_meta.x, df_meta.y),
        crs=gdf_zwalmbeek.crs,
    )
    gdf_plot = pd.concat(
        [
            gdf_zwalmbeek.dissolve()[["NAAM", "geometry"]].rename(
                columns={"NAAM": "id"}
            ),
            gdf_meta[["id", "geometry"]],
        ],
        ignore_index=True,
    ).drop_duplicates()
    # Ordered Categorical to prevent alphabetical sorting
    gdf_plot["id"] = pd.Categorical(
        gdf_plot["id"], categories=gdf_plot["id"].unique(), ordered=True
    )

    fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)
    gdf_plot.plot(
        ax=ax,
        column="id",
        cmap="jet",
        legend=True,
        legend_kwds={"loc": "lower right"},
    )
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.ticklabel_format(useMathText=True, scilimits=(0, 0))
    cx.add_basemap(
        ax, source=MAP_SOURCE, crs=gdf_meta.crs, attribution_size=ATTRIBUTION_TEXT_SIZE
    )
    save(fig, FILENAME_FIG_WATERINFO_SITES)


def plot_ssm_original():
    ds_ssm = xr.open_dataset(
        SATELLITE_SOIL_MOISTURE_PROCESSED_DIR / "satellite_soil_moisture_unfiltered.nc",
        decode_coords="all",
    )
    ds_ssm = ds_ssm.rio.reproject("EPSG:31370")
    da_ssm_plot = ds_ssm.isel(time=10)[VARIABLE_NAME_SATELLITE_SOIL_MOISTURE]

    fig, ax = plt.subplots(figsize=(4, 4), constrained_layout=True)
    da_ssm_plot.plot(
        ax=ax, alpha=0.9, cbar_kwargs={"label": "surface soil moisture [%]"}
    )
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.ticklabel_format(useMathText=True, scilimits=(0, 0))
    ax.set_title(f"{da_ssm_plot.time.dt.date.values}")
    cx.add_basemap(
        ax,
        source=MAP_SOURCE,
        crs=ds_ssm.rio.crs,
        attribution_size=ATTRIBUTION_TEXT_SIZE,
    )
    save(fig, FILENAME_FIG_SSM_ORIGINAL)


def main():
    FIGURES_STUDY_AREA_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use(ROOT_PATH / "figurestyling.mplstyle")
    gdf_vha = gpd.read_file(CATCHMENT_INFO_PROCESSED_DIR / FILENAME_VHA)
    gdf_zwalmbeek = gdf_vha[gdf_vha["NAAM"] == "Zwalmbeek"]
    plot_zwalmbeek(gdf_zwalmbeek)
    plot_waterinfo_sites(gdf_zwalmbeek)
    plot_ssm_original()


# %% Execution

if __name__ == "__main__":
    main()

# %%
