import os
import json
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


#df=pd.read_csv("assets/2019.csv")

data=pd.read_json("assets/data.json")
state_names = data["state"]
with open("assets/laender_999_geo.json", "r", encoding="utf-8") as file:
    geojson_data = json.load(file)


app=dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.Div(className='app-header',children=[
        html.H1("Statistics of volunteering in Austria",className='display-3')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="metric-dropdown",
                options=[
                    {'label':'All volunteers','value':'perc_volunteers_from_pop'},
                    {'label':'Formal volunteers','value':'perc_formal_from_pop'},
                    {'label':'Informal volunteers','value':'perc_informal_from_pop'}
                ],
                value='perc_volunteers_from_pop',
                style={'width':'100%'}
            )
        ],width={'size':6,'offset':3},className='dropdown-container')
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='austria-map'),width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='data-insights',className='data-insights'),
            html.Div(id='top-bottom-countries',className='top-bottom-countries')
        ],width=8),
        dbc.Col([html.Div(id='Region-details',className='country-details')],width=4)
    ])

],fluid=True)

#creating callbacks 
#austria map callback, take volunteer type inpit to update map
@app.callback(
    Output('austria-map','figure'),
    Input('metric-dropdown','value')
)
def update_map(selected_metric):
    fig = px.choropleth(
        data,
        locations="state",
        geojson=geojson_data,
        color=selected_metric,
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        title=f"Volunteering in Austria:{selected_metric}"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":40})
    fig.update_geos(fitbounds="locations", visible=False)  # Adjust map view
    return fig

#top and bottom regions

@app.callback(
    Output('data-insights','children'),
    Input('metric-dropdown','value')
)
def update_insights(selected_metric):
    print(f"Selected Metric: {selected_metric}")
    highest=data.loc[data[selected_metric].idxmax()]
    lowest=data.loc[data[selected_metric].idxmin()]

    insights = [
        html.H3(f"Highest:{selected_metric}:{highest['state']}({highest[selected_metric]})"),
        html.H3(f"Lowest:{selected_metric}:{lowest['state']}({lowest[selected_metric]})")
    ]
    return insights

# Run the Dash app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if no PORT variable is found
    app.run_server(host="0.0.0.0", port=port, debug=False)