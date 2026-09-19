import plotly.graph_objects as go

def add_line_layer(fig, layer, name, width=2):
    if layer is None or layer.empty:
        return

    lon = []
    lat = []

    for geometry in layer.geometry:
        if geometry is None:
            continue

        if geometry.geom_type == "LineString":
            x, y = geometry.xy
            lon.extend(x)
            lat.extend(y)
            lon.append(None)
            lat.append(None)

        elif geometry.geom_type == "MultiLineString":
            for line in geometry.geoms:
                x, y = line.xy
                lon.extend(x)
                lat.extend(y)
                lon.append(None)
                lat.append(None)

    fig.add_trace(go.Scattermapbox(lon=lon, lat=lat, mode="lines", name=name, line={"width": width}))

def add_point_layer(fig, layer, name):
    if layer is None or layer.empty:
        return

    lon = []
    lat = []

    for geometry in layer.geometry:
        if geometry is None:
            continue

        if geometry.geom_type == "Point":
            lon.append(geometry.x)
            lat.append(geometry.y)

        elif geometry.geom_type == "MultiPoint":
            for point in geometry.geoms:
                lon.append(point.x)
                lat.append(point.y)

    fig.add_trace(go.Scattermapbox(lon=lon, lat=lat, mode="markers", name=name, marker={"size": 8}))

def add_polygon_layer(fig, layer, name):
    if layer is None or layer.empty:
        return

    boundary = layer.boundary
    lon = []
    lat = []

    for geometry in boundary:
        if geometry is None:
            continue

        if geometry.geom_type == "LineString":
            x, y = geometry.xy
            lon.extend(x)
            lat.extend(y)
            lon.append(None)
            lat.append(None)

        elif geometry.geom_type == "MultiLineString":
            for line in geometry.geoms:
                x, y = line.xy
                lon.extend(x)
                lat.extend(y)
                lon.append(None)
                lat.append(None)

    fig.add_trace(go.Scattermapbox(lon=lon, lat=lat, mode="lines", name=name))

def add_layer(fig, layer, name):
    if layer is None or layer.empty:
        return

    geometry_types = set(layer.geometry.geom_type.unique())

    if geometry_types.intersection({"Point", "MultiPoint"}):
        add_point_layer(fig, layer, name)

    elif geometry_types.intersection({"LineString", "MultiLineString"}):
        width = 4 if name == "Principal Arterials" else 2
        add_line_layer(fig, layer, name, width)

    else:
        add_polygon_layer(fig, layer, name)

def build_map(layers, selected_layers):
    fig = go.Figure()

    aoi = layers.get("AOI")
    add_polygon_layer(fig, aoi, "Boulder Boundary")

    for name in selected_layers:
        add_layer(fig, layers.get(name), name)

    fig.update_layout(
        mapbox={"style": "open-street-map", "center": {"lat": 40.015, "lon": -105.270}, "zoom": 11},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=650
    )

    return fig