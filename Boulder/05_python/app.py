from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

from data_loader import load_all_layers
from map_builder import build_map
from analysis import calculate_statistics

layers = load_all_layers()
stats = calculate_statistics(layers)

app = Dash(__name__)

available_layers = [
    name for name in layers
    if name != "AOI" and layers[name] is not None
]

app.layout = html.Div([

    html.H1("Boulder GEOINT Dashboard"),

    html.P("How have terrain and water influenced the development and transportation structure of Boulder, Colorado?"),

    html.Div([
        html.Div([
            html.H3("Buildings"),
            html.P(f"{stats['Buildings']:,}")
        ]),

        html.Div([
            html.H3("Transit Stops"),
            html.P(f"{stats['Transit Stops']:,}")
        ]),

        html.Div([
            html.H3("Schools"),
            html.P(f"{stats['Schools']:,}")
        ]),

        html.Div([
            html.H3("Fire Stations"),
            html.P(f"{stats['Fire Stations']:,}")
        ]),

        html.Div([
            html.H3("Bridges"),
            html.P(f"{stats['Bridges']:,}")
        ])
    ]),

    html.H3("Map Layers"),

    dcc.Checklist(
        id="layer-selector",
        options=[{"label": name, "value": name} for name in available_layers],
        value=["Streams & Rivers", "Principal Arterials", "Buildings"]
    ),

    dcc.Graph(id="geoint-map"),

    html.H3("Infrastructure"),

    dcc.Graph(id="infrastructure-chart")
])

@app.callback(
    Output("geoint-map", "figure"),
    Input("layer-selector", "value")
)
def update_map(selected_layers):
    return build_map(layers, selected_layers)

@app.callback(
    Output("infrastructure-chart", "figure"),
    Input("layer-selector", "value")
)
def update_chart(selected_layers):
    names = list(stats.keys())
    values = list(stats.values())

    fig = go.Figure(go.Bar(x=names, y=values))
    fig.update_layout(title="Selected Infrastructure Feature Counts", xaxis_title="Feature", yaxis_title="Count")

    return fig

if __name__ == "__main__":
    app.run(debug=True)