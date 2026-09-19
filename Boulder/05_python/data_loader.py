from pathlib import Path
import geopandas as gpd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "03_processes_data"

def load_layer(filename):
    path = DATA_DIR / filename

    if not path.exists():
        print(f"Missing: {filename}")
        return None

    try:
        layer = gpd.read_file(path)

        if layer.crs is not None:
            layer = layer.to_crs("EPSG:4326")

        print(f"Loaded: {filename}")
        return layer

    except Exception as error:
        print(f"Error loading {filename}: {error}")
        return None

def load_all_layers():
    layers = {
        "AOI": load_layer("Boulder_AOI.gpkg"),
        "Contours": load_layer("Boulder_Contours_20ft.gpkg"),
        "Streams & Rivers": load_layer("Boulder_Streams_Rivers.gpkg"),
        "Buildings": load_layer("Boulder_Buildings.gpkg"),
        "Principal Arterials": load_layer("Boulder_Principal_Arterials.gpkg"),
        "Minor Arterials": load_layer("Boulder_Minor_Arterials.gpkg"),
        "Open Space": load_layer("Boulder_Open_Space.gpkg"),
        "Flood Hazard": load_layer("Boulder_Flood_Hazard.gpkg"),
        "Bridges": load_layer("Boulder_Bridges.gpkg"),
        "Transit Stops": load_layer("Boulder_Transit_Stops.gpkg"),
        "Schools": load_layer("Boulder_Schools.gpkg"),
        "Fire Stations": load_layer("Boulder_Fire_Stations.gpkg")
    }

    return layers