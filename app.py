import os
import json
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
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
        dbc.Col([
            dcc.RadioItems(
                id="stat-type-radio",
                options=[
                    {'label': 'Percentage of Volunteers', 'value': 'perc'},
                    {'label': 'Average Hours per Week', 'value': 'avg_hours'},
                    {'label': 'Median Hours per Week', 'value': 'median_hours'}
                ],
                value='perc',
                labelStyle={'display': 'block'}
            )
        ], width={'size': 4, 'offset': 4})
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='austria-map',config={'displayModeBar': False},clickData=None,clear_on_unhover=True),width=6)
        ,
        dbc.Col(dcc.Graph(id='region-boxplot'), width=6)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='data-insights',className='data-insights')
            #,html.Div(id='top-bottom-countries',className='top-bottom-countries')
        ],width=8),
        dbc.Col([html.Div(id='Region-details',className='country-details')],width=4)
    ])

,dcc.Store(id='selected-region', data='Austria')],fluid=True)

#creating callbacks 
#austria map callback, take volunteer type input to update map

# Mapping logic for stat fields
def resolve_column(metric_value, stat_type_value):
    # Extract the base key
    if metric_value == 'perc_volunteers_from_pop':
        base = 'vlntrs'
    elif metric_value == 'perc_formal_from_pop':
        base = 'formal'
    elif metric_value == 'perc_informal_from_pop':
        base = 'informal'
    else:
        base = 'vlntrs'  # fallback

    if stat_type_value == 'perc':
        return metric_value  # already correct
    elif stat_type_value == 'avg_hours':
        return f'avg_hours_{base}'
    elif stat_type_value == 'median_hours':
        return f'median_hours_{base}'
    else:
        return metric_value

@app.callback(
    Output('region-boxplot', 'figure'),
    Output('austria-map', 'figure'),
    Output('selected-region', 'data'),
    Input('austria-map', 'clickData'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value'),
    State('selected-region', 'data'),
)
def update_visuals(click_data, metric_value, stat_type, current_region):
    import plotly.graph_objects as go

    # Determine new selected region
    new_region = current_region  # Default to last selected
# 👇 Only update region if the user has actually clicked a new region
    if click_data and click_data.get('points'):
        clicked_region = click_data['points'][0]['location']
        if clicked_region != current_region:
            new_region = clicked_region


    # Fallback if something went wrong
    if new_region not in data['state'].values:
        new_region = 'Austria'

    # Determine prefix for the column
    prefix = {
        'perc_volunteers_from_pop': 'vlntrs',
        'perc_formal_from_pop': 'formal',
        'perc_informal_from_pop': 'informal'
    }[metric_value]

    # --- Boxplot ---
    q1 = data.loc[data['state'] == new_region, f'25_hrs_{prefix}'].values[0]
    median = data.loc[data['state'] == new_region, f'median_hours_{prefix}'].values[0]
    q3 = data.loc[data['state'] == new_region, f'75_hrs_{prefix}'].values[0]

    fig_box = go.Figure()
    fig_box.add_trace(go.Scatter(
        x=[q1, q3], y=['Distribution'], mode='lines',
        line=dict(color='lightblue', width=12), name='25th–75th Percentile'
    ))
    fig_box.add_trace(go.Scatter(
        x=[median], y=['Distribution'], mode='markers',
        marker=dict(color='black', size=10), name='Median'
    ))
    fig_box.update_layout(
        title=f"Volunteer Hours – {new_region}",
        xaxis_title="Hours per Week",
        yaxis=dict(showticklabels=False),
        margin=dict(t=40, l=20, r=20, b=20),
        height=300
    )

    # --- Choropleth Map ---
    column = resolve_column(metric_value, stat_type)
    fig_map = px.choropleth(
        data,
        locations="state",
        geojson=geojson_data,
        color=column,
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        title=f"Volunteering Map ({metric_value})"
    )

    # Highlight and zoom only if specific region is selected
    if new_region != 'Austria':
        selected_feature = next(
            (f for f in geojson_data['features'] if f['properties']['name'] == new_region), None
        )
        if selected_feature:
            coords = selected_feature['geometry']['coordinates'][0][0]
            lons, lats = zip(*coords)
            fig_map.update_geos(
                lonaxis_range=[min(lons), max(lons)],
                lataxis_range=[min(lats), max(lats)],
                visible=False
            )

    else:
        fig_map.update_geos(fitbounds="locations", visible=False)

    fig_map.update_traces(
        marker_line_color="black",
        marker_line_width=0.5,
        selector=dict(type='choropleth')
    )

    return fig_box, fig_map, new_region




'''def update_map(metric_dropdown_value, stat_type_value):
    column = resolve_column(metric_dropdown_value, stat_type_value)

    title_map = {
        'perc': 'Percentage of Volunteers',
        'avg_hours': 'Average Hours per Week',
        'median_hours': 'Median Hours per Week'
    }

    title_text = f"{column.replace('_', ' ').capitalize()} – {title_map[stat_type_value]}"

    fig = px.choropleth(
        data,
        locations="state",
        geojson=geojson_data,
        color=column,
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        title=title_text
    )

    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 40})
    fig.update_geos(fitbounds="locations", visible=False)

    return fig
'''


@app.callback(
    Output('data-insights', 'children'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value')
)
def update_insights(metric_dropdown_value, stat_type_value):
    column = resolve_column(metric_dropdown_value, stat_type_value)

    highest = data.loc[data[column].idxmax()]
    lowest = data.loc[data[column].idxmin()]

    label_map = {
        'perc': '% of Population',
        'avg_hours': 'Average Weekly Hours',
        'median_hours': 'Median Weekly Hours'
    }

    return [
        html.H3(f"Highest: {highest['state']} ({highest[column]} {label_map[stat_type_value]})"),
        html.H3(f"Lowest: {lowest['state']} ({lowest[column]} {label_map[stat_type_value]})")
    ]



# Run the Dash app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if no PORT variable is found
    app.run_server(host="0.0.0.0", port=port, debug=False)