import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

data=pd.read_json("assets/data.json")
#geo_data=pd.read_json("assets/laender_999_geo.json")

app=dash.Dash(__name__)

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)