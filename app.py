import os
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

data=pd.read_json("assets/data.json")
#geo_data=pd.read_json("assets/laender_999_geo.json")

app=dash.Dash(__name__)
server = app.server

# Run the Dash app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if no PORT variable is found
    app.run_server(host="0.0.0.0", port=port, debug=False)