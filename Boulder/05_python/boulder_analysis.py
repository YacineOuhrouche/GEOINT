# ============================================================
# BOULDER GEOINT PROJECT — PYTHON ANALYSIS
# ============================================================

from pathlib import Path

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT SETUP
# ============================================================

print("\n========================================")
print("BOULDER GEOINT ANALYSIS")
print("========================================")

print(
    "\nMain Intelligence Question:\n"
    "How have terrain and water influenced the development "
    "and transportation structure of Boulder, Colorado?"
)

# This assumes the script is inside:
# project_folder/05_python/boulder_analysis.py

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "03_processes_data"
CHART_DIR = PROJECT_DIR / "07_charts"
MAP_DIR = PROJECT_DIR / "06_maps"

CHART_DIR.mkdir(exist_ok=True)
MAP_DIR.mkdir(exist_ok=True)

TARGET_CRS = "EPSG:26913"

print(f"\nProject folder: {PROJECT_DIR}")
print(f"Data folder: {DATA_DIR}")


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def find_file(*names):
    """
    Find the first existing filename from a list of possibilities.
    Returns None if nothing exists.
    """
    for name in names:
        path = DATA_DIR / name
        if path.exists():
            return path

    return None


def load_layer(name, *filenames):
    """
    Load a GeoPackage safely.
    """
    path = find_file(*filenames)

    if path is None:
        print(f"\n[SKIPPED] {name}: file not found.")
        return None

    try:
        layer = gpd.read_file(path)

        print(f"\n{name}")
        print("-" * len(name))
        print(f"File: {path.name}")
        print(f"Features: {len(layer)}")
        print(f"CRS: {layer.crs}")
        print(f"Geometry types: {layer.geometry.geom_type.unique()}")
        print(f"Bounds: {layer.total_bounds}")

        return layer

    except Exception as error:
        print(f"\n[ERROR] Could not load {name}")
        print(error)
        return None


def standardize_crs(layer, name):
    """
    Reproject a correctly-defined layer into EPSG:26913.
    """
    if layer is None:
        return None

    if layer.crs is None:
        print(f"[WARNING] {name} has no CRS.")
        return layer

    try:
        if layer.crs.to_string() != TARGET_CRS:
            print(f"{name}: reprojecting {layer.crs} -> {TARGET_CRS}")
            layer = layer.to_crs(TARGET_CRS)

        return layer

    except Exception as error:
        print(f"[WARNING] Could not reproject {name}: {error}")
        return layer


def check_bounds(layer, name):
    """
    Basic diagnostic for the CRS problem noticed in QGIS.

    Approximate UTM 13N coordinates around Boulder should generally
    be near X = 450,000–520,000 and Y = 4,400,000–4,460,000.
    """
    if layer is None or layer.empty:
        return

    minx, miny, maxx, maxy = layer.total_bounds

    print(f"\nCRS check — {name}")

    if (
        400000 <= minx <= 600000
        and 400000 <= maxx <= 600000
        and 4300000 <= miny <= 4600000
        and 4300000 <= maxy <= 4600000
    ):
        print("Coordinates look reasonable for Boulder in EPSG:26913.")

    else:
        print(
            "WARNING: Coordinates do not look typical for Boulder "
            "in EPSG:26913."
        )
        print(
            "This layer may have been assigned the wrong CRS "
            "before it was exported."
        )


# ============================================================
# 3. LOAD DATA
# ============================================================

aoi = load_layer(
    "Boulder AOI",
    "Boulder_AOI.gpkg",
    "Boulder_AOI_new.gpkg"
)

contours = load_layer(
    "20 ft Contours",
    "Boulder_Contours_20ft.gpkg"
)

streams = load_layer(
    "Streams and Rivers",
    "Boulder_Streams_Rivers.gpkg"
)

buildings = load_layer(
    "Buildings",
    "Boulder_Buildings.gpkg"
)

principal_roads = load_layer(
    "Principal Arterials",
    "Boulder_Principal_Arterials.gpkg"
)

minor_roads = load_layer(
    "Minor Arterials",
    "Boulder_Minor_Arterials.gpkg"
)

open_space = load_layer(
    "Open Space",
    "Boulder_Open_Space.gpkg"
)

flood = load_layer(
    "Flood Hazard",
    "Boulder_Flood_Hazard.gpkg"
)

bridges = load_layer(
    "Bridges",
    "Boulder_Bridges.gpkg"
)

transit_stops = load_layer(
    "Transit Stops",
    "Boulder_Transit_Stops.gpkg",
    "Boulder_Transit_Stops_26913.gpkg"
)


# ============================================================
# 4. CRS STANDARDIZATION
# ============================================================

layers = {
    "AOI": aoi,
    "Contours": contours,
    "Streams": streams,
    "Buildings": buildings,
    "Principal Roads": principal_roads,
    "Minor Roads": minor_roads,
    "Open Space": open_space,
    "Flood Hazard": flood,
    "Bridges": bridges,
    "Transit Stops": transit_stops,
}

for name, layer in layers.items():
    layers[name] = standardize_crs(layer, name)


aoi = layers["AOI"]
contours = layers["Contours"]
streams = layers["Streams"]
buildings = layers["Buildings"]
principal_roads = layers["Principal Roads"]
minor_roads = layers["Minor Roads"]
open_space = layers["Open Space"]
flood = layers["Flood Hazard"]
bridges = layers["Bridges"]
transit_stops = layers["Transit Stops"]


# ============================================================
# 5. CRS / LOCATION DIAGNOSTIC
# ============================================================

print("\n========================================")
print("CRS / LOCATION DIAGNOSTIC")
print("========================================")

for name, layer in layers.items():
    check_bounds(layer, name)


# ============================================================
# 6. TERRAIN ANALYSIS
# ============================================================

print("\n========================================")
print("TERRAIN ANALYSIS")
print("========================================")

if contours is not None:

    print("\nContour columns:")
    print(list(contours.columns))

    possible_elevation_fields = [
        "ELEVATION",
        "Elevation",
        "elevation",
        "ELEV",
        "Elev",
        "CONTOUR",
        "Contour",
        "Z",
    ]

    elevation_field = None

    for field in possible_elevation_fields:
        if field in contours.columns:
            elevation_field = field
            break

    if elevation_field is not None:

        elevations = pd.to_numeric(
            contours[elevation_field],
            errors="coerce"
        ).dropna()

        if not elevations.empty:

            min_elevation = elevations.min()
            max_elevation = elevations.max()
            relief = max_elevation - min_elevation

            print(f"\nMinimum elevation: {min_elevation:.0f} ft")
            print(f"Maximum elevation: {max_elevation:.0f} ft")
            print(f"Mapped relief: {relief:.0f} ft")

        else:
            print("Elevation column exists but contains no usable numbers.")

    else:
        print(
            "\nElevation field was not detected automatically."
        )
        print(
            "From the QGIS inspection, the observed contour range was "
            "approximately 5,060–5,940 ft."
        )


# ============================================================
# 7. SIMPLE FEATURE STATISTICS
# ============================================================

print("\n========================================")
print("FEATURE STATISTICS")
print("========================================")

if buildings is not None:
    print(f"Building features: {len(buildings):,}")

if streams is not None:

    stream_copy = streams.copy()

    try:
        stream_copy["length_km"] = stream_copy.geometry.length / 1000

        total_stream_length = stream_copy["length_km"].sum()

        print(
            f"Total mapped stream/river length: "
            f"{total_stream_length:.2f} km"
        )

    except Exception as error:
        print(f"Could not calculate stream length: {error}")


if principal_roads is not None:

    roads_copy = principal_roads.copy()

    try:
        roads_copy["length_km"] = roads_copy.geometry.length / 1000

        print(
            f"Principal arterial length: "
            f"{roads_copy['length_km'].sum():.2f} km"
        )

    except Exception as error:
        print(f"Could not calculate road length: {error}")


if open_space is not None:

    open_copy = open_space.copy()

    try:
        open_copy["area_km2"] = open_copy.geometry.area / 1_000_000

        print(
            f"Mapped open-space area: "
            f"{open_copy['area_km2'].sum():.2f} km²"
        )

    except Exception as error:
        print(f"Could not calculate open-space area: {error}")


# ============================================================
# 8. TRANSIT PROXIMITY ANALYSIS
# ============================================================

print("\n========================================")
print("TRANSIT PROXIMITY ANALYSIS")
print("========================================")

transit_buffer = None

if transit_stops is not None:

    try:
        transit_buffer = transit_stops.copy()

        transit_buffer["geometry"] = transit_buffer.geometry.buffer(500)

        transit_buffer = transit_buffer.dissolve()

        output_path = (
            DATA_DIR /
            "Boulder_Transit_Stops_500m_Buffer_Python.gpkg"
        )

        transit_buffer.to_file(
            output_path,
            driver="GPKG"
        )

        print("Created 500 m transit-stop buffer.")
        print(f"Saved to: {output_path}")

    except Exception as error:
        print(f"Transit buffer analysis failed: {error}")


# ============================================================
# 9. MULTI-LAYER ANALYTICAL MAP
# ============================================================

print("\n========================================")
print("CREATING ANALYTICAL MAP")
print("========================================")

fig, ax = plt.subplots(figsize=(10, 10))

something_plotted = False


if open_space is not None:
    open_space.plot(
        ax=ax,
        alpha=0.25
    )
    something_plotted = True


if flood is not None:
    flood.plot(
        ax=ax,
        alpha=0.30
    )
    something_plotted = True


if contours is not None:
    contours.plot(
        ax=ax,
        linewidth=0.25,
        alpha=0.35
    )
    something_plotted = True


if buildings is not None:
    buildings.plot(
        ax=ax,
        linewidth=0.1,
        alpha=0.45
    )
    something_plotted = True


if streams is not None:
    streams.plot(
        ax=ax,
        linewidth=1.2
    )
    something_plotted = True


if minor_roads is not None:
    minor_roads.plot(
        ax=ax,
        linewidth=0.7
    )
    something_plotted = True


if principal_roads is not None:
    principal_roads.plot(
        ax=ax,
        linewidth=1.5
    )
    something_plotted = True


if bridges is not None:
    bridges.plot(
        ax=ax,
        markersize=18
    )
    something_plotted = True


if aoi is not None:
    aoi.boundary.plot(
        ax=ax,
        linewidth=2
    )
    something_plotted = True


if something_plotted:

    ax.set_title(
        "Boulder — Terrain, Water, Development and Transportation"
    )

    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.set_aspect("equal")

    plt.tight_layout()

    analytical_map_path = (
        MAP_DIR /
        "Boulder_Analytical_Map_Python.png"
    )

    plt.savefig(
        analytical_map_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Map saved to: {analytical_map_path}")

    plt.show()

else:
    print("No usable layers were available for the map.")


# ============================================================
# 10. SIMPLE STATISTICS CHART
# ============================================================

statistics = {}

if buildings is not None:
    statistics["Buildings"] = len(buildings)

if bridges is not None:
    statistics["Bridges"] = len(bridges)

if transit_stops is not None:
    statistics["Transit Stops"] = len(transit_stops)


if statistics:

    plt.figure(figsize=(8, 5))

    plt.bar(
        statistics.keys(),
        statistics.values()
    )

    plt.title("Selected Infrastructure Feature Counts")
    plt.ylabel("Number of Features")

    plt.tight_layout()

    chart_path = (
        CHART_DIR /
        "Boulder_Infrastructure_Counts.png"
    )

    plt.savefig(
        chart_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"\nChart saved to: {chart_path}")

    plt.show()


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n========================================")
print("ANALYSIS COMPLETE")
print("========================================")

print(
    """
Initial GEOINT interpretation:

1. Boulder has strong west-to-east terrain variation.
2. Steeper western terrain constrains intensive development.
3. Streams and flood-prone areas create additional spatial constraints.
4. Buildings and transportation infrastructure are concentrated mainly
   across the more accessible developed portions of the city.
5. Major roads generally follow terrain that is easier to traverse.
6. Open space reinforces the development boundary along parts of the
   western side of Boulder.

These findings should be verified against the final QGIS maps before
being used as final report conclusions.
"""
)