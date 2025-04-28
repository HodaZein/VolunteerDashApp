import os
import json
import dash
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

trend_data = pd.read_json("assets/volunteering_time_series_fake.json")  # Adjust path if needed

data = pd.read_json("assets/data.json")
with open("assets/laender_999_geo.json", "r", encoding="utf-8") as file:
    geojson_data = json.load(file)

YEARS = sorted(data['year'].unique())
STATES = data['state'].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    # General page title
    html.H1("Statistics of volunteering in Austria", className="text-center my-4 fw-bold"),
    # Collapse-able Sidebar
    # Top-left Menu Button + Sidebar
    html.Div([
        dbc.Button(
            "☰",  # Contents Icon
            id="open-offcanvas",
            n_clicks=0,
            color="light",
            style={"position": "fixed", "top": "20px", "left": "20px", "zIndex": 9999, "fontSize": "24px"}
        ),
        dbc.Offcanvas(
            [
                html.H5("Contents", className="my-3"),
                dbc.Nav([
                    dbc.NavLink("Geographic Distribution", href="#choropleth-card", external_link=True),
                    dbc.NavLink("Time-Series Trends", href="#timeseries-card", external_link=True),
                    # Add more links as needed
                ], vertical=True)
            ],
            id="offcanvas",
            is_open=False,
            placement="start",   # Sidebar opens from the left
            backdrop=True,       # Dim background when open
            style={"width": "250px", "backgroundColor": "white"},
        ),
    ]),

    dbc.Card([
        dbc.CardBody([
            html.H4("Geographic Distribution of Volunteering", className="mb-4 mt-2 text-center fw-semibold"),
            
            # Filters in one row, well-spaced
            dbc.Row([
                dbc.Col([
                    html.Label("Type of Volunteering", className="mb-1"),
                    dcc.Dropdown(
                        id="metric-dropdown",
                        options=[
                            {'label': 'Any', 'value': 'perc_volunteers_from_pop'},
                            {'label': 'Formal', 'value': 'perc_formal_from_pop'},
                            {'label': 'Informal', 'value': 'perc_informal_from_pop'}
                        ],
                        value='perc_volunteers_from_pop',
                        style={'width': '100%'}
                    ),
                ], width=3),

                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="stat-type-radio",
                        options=[
                            {'label': 'Percentage', 'value': 'perc'},
                            {'label': 'Avg Hours', 'value': 'avg_hours'},
                            {'label': 'Median Hours', 'value': 'median_hours'}
                        ],
                        value='perc',
                        labelStyle={'marginRight': '15px'}
                    ),
                ], width=3, style={'paddingTop': 8}),

                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Slider(
                        id='year-slider',
                        min=int(min(YEARS)),
                        max=int(max(YEARS)),
                        value=int(max(YEARS)),
                        marks={int(y): str(int(y)) for y in YEARS},
                        step=None,
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ], width=4, style={'paddingTop': 12}),
                
                dbc.Col([
                    dbc.Button("Reset to Austria", id="reset-button", color="primary", className="mt-3")
                ], width=2, style={'textAlign': 'right', 'paddingTop': 18}),
            ], className='mb-4', align="center", style={ "borderRadius": "0.5rem", "padding": "14px"}),

            dbc.Row([
                dbc.Col(dcc.Graph(id='austria-map', config={'displayModeBar': False}), width=6),
                dbc.Col(dcc.Graph(id='region-boxplot'), width=6)
            ]),
            dbc.Row([
                dbc.Col(html.Div(id='data-insights', className='data-insights'), width=12),
            ])
        ])
    ],id="choropleth-card", className="mb-5 shadow-sm border-0"),
    # ... your existing layout above ...

    # ---- Time Series Card ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Time-series of Volunteering in Austria", className="mb-4 mt-2 text-center fw-semibold"),
            dbc.Row([
                dbc.Col([
                    html.Label("Type of Volunteering", className="mb-1"),
                    dcc.Dropdown(
                        id="ts-type-dropdown",
                        options=[
                            {'label': 'Any', 'value': 'any'},
                            {'label': 'Formal', 'value': 'formal'},
                            {'label': 'Informal', 'value': 'informal'},
                            {'label': 'Both formal and informal', 'value': 'both_formal_and_informal'},
                            {'label': 'Formal only', 'value': 'formal_only'},
                            {'label': 'Informal only', 'value': 'informal_only'},
                        ],
                        value='any',
                        clearable=False
                    )
                ], width=3),                
                dbc.Col([
                    html.Label("Demographic", className="mb-1"),
                    dcc.Dropdown(
                        id="ts-demographic-dropdown",
                        options=[{'label': d.capitalize().replace("_", " "), 'value': d}
                                for d in sorted(trend_data['demographic'].unique())],
                        value='age',  # Set your preferred default
                        clearable=False
                    )
                ], width=3),
                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="ts-radio",
                        options=[
                            {'label': 'Percentage', 'value': 'perc'},
                            {'label': 'Count', 'value': 'count'}
                        ],
                        value='perc',
                        labelStyle={'marginRight': '15px'}
                    )
                ], width=2, style={'paddingTop': 8}),
                dbc.Col([
                    html.Label("Year Range", className="mb-1"),
                    dcc.RangeSlider(
                        id="ts-year-slider",
                        min=int(trend_data['year'].min()),
                        max=int(trend_data['year'].max()),
                        value=[int(trend_data['year'].min()), int(trend_data['year'].max())],
                        marks={int(y): str(int(y)) for y in sorted(trend_data['year'].unique())},
                        step=None
                    )
                ], width=4, style={'paddingTop': 12})
            ], className='mb-4', align="center"),
            dcc.Graph(id="ts-line-graph")
        ])
    ],id="timeseries-card", className="mb-5 shadow-sm border-0"),
    # ...rest of your layout (e.g., other cards below)...


    # dcc.Store for region selection
    dcc.Store(id='selected-region', data='Austria'),

    # Placeholder for future visualisations
    html.Div(id="other-sections-placeholder"),
], fluid=True)

def resolve_column(metric_value, stat_type_value):
    if metric_value == 'perc_volunteers_from_pop':
        base = 'vlntrs'
    elif metric_value == 'perc_formal_from_pop':
        base = 'formal'
    elif metric_value == 'perc_informal_from_pop':
        base = 'informal'
    else:
        base = 'vlntrs'
    if stat_type_value == 'perc':
        return metric_value
    elif stat_type_value == 'avg_hours':
        return f'avg_hours_{base}'
    elif stat_type_value == 'median_hours':
        return f'median_hours_{base}'
    else:
        return metric_value
    

@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    State("offcanvas", "is_open"),
)
def toggle_offcanvas(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output('region-boxplot', 'figure'),
    Output('austria-map', 'figure'),
    Output('selected-region', 'data'),
    Input('austria-map', 'clickData'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value'),
    Input('year-slider', 'value'),
    Input('reset-button', 'n_clicks'),
    State('selected-region', 'data'),
    prevent_initial_call=False
)
def update_visuals(click_data, metric_value, stat_type, year, reset_clicks, current_region):
    import plotly.graph_objects as go

    # Context-aware region selection logic
    triggered = ctx.triggered_id
    if triggered == "reset-button":
        new_region = "Austria"
    elif triggered == "austria-map" and click_data and click_data.get('points') and 'location' in click_data['points'][0]:
        new_region = click_data['points'][0]['location']
    elif current_region in STATES:
        new_region = current_region
    else:
        new_region = "Austria"

    # Filter data for year
    d_year = data[data['year'] == int(year)]

    prefix = {
        'perc_volunteers_from_pop': 'vlntrs',
        'perc_formal_from_pop': 'formal',
        'perc_informal_from_pop': 'informal'
    }[metric_value]

    # --- Boxplot ---
    if new_region not in d_year['state'].values:
        new_region = "Austria"
    q1 = d_year.loc[d_year['state'] == new_region, f'25_hrs_{prefix}'].values[0]
    median = d_year.loc[d_year['state'] == new_region, f'median_hours_{prefix}'].values[0]
    q3 = d_year.loc[d_year['state'] == new_region, f'75_hrs_{prefix}'].values[0]

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
        title=f"Volunteer Hours Boxplot– {new_region} ({year})",
        xaxis_title="Hours per Week",
        yaxis=dict(showticklabels=False),
        margin=dict(t=130, l=20, r=20, b=20),
        height=300

    )

    # --- Choropleth Map ---
    column = resolve_column(metric_value, stat_type)
    fig_map = px.choropleth(
        d_year,
        locations="state",
        geojson=geojson_data,
        color=column,
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        title=f"Volunteering Map ({year})"

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

@app.callback(
    Output('data-insights', 'children'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value'),
    Input('year-slider', 'value'),
)
def update_insights(metric_dropdown_value, stat_type_value, year):
    column = resolve_column(metric_dropdown_value, stat_type_value)
    d_year = data[data['year'] == int(year)]

    highest = d_year.loc[d_year[column].idxmax()]
    lowest = d_year.loc[d_year[column].idxmin()]

    label_map = {
        'perc': '% of Population',
        'avg_hours': 'Average Weekly Hours',
        'median_hours': 'Median Weekly Hours'
    }

    return [
        html.H4(f"Year: {year}"),
        html.H5(f"Highest: {highest['state']} ({highest[column]} {label_map[stat_type_value]})"),
        html.H5(f"Lowest: {lowest['state']} ({lowest[column]} {label_map[stat_type_value]})")
    ]


@app.callback(
    Output("ts-line-graph", "figure"),
    Input("ts-demographic-dropdown", "value"),
    Input("ts-type-dropdown", "value"),
    Input("ts-radio", "value"),
    Input("ts-year-slider", "value"),
)
def update_time_series(demographic, volunteer_type, show_type, year_range):
    d = trend_data[
        (trend_data['demographic'] == demographic) &
        (trend_data['year'] >= year_range[0]) &
        (trend_data['year'] <= year_range[1])
    ]
    categories = d['category'].unique()
    fig = px.line()
    for cat in categories:
        subset = d[d['category'] == cat].sort_values('year')
        if show_type == 'perc':
            y_col = f"{volunteer_type}_volunteer_perc"
            y_label = "Percentage of Volunteers"
        else:
            y_col = f"{volunteer_type}_volunteer_count"
            y_label = "Number of Volunteers"
        fig.add_scatter(
            x=subset['year'],
            y=subset[y_col],
            mode='lines+markers',
            name=cat
        )
    fig.update_layout(
        title="Trends in Volunteering by Demographic",
        xaxis_title="Year",
        yaxis_title=y_label,
        legend_title="Category",
        margin=dict(t=60, l=20, r=20, b=20),
        height=450,
        template="plotly_white"
    )
    return fig


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
