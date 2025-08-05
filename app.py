import os
import json
import dash
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


# Loading JSON files
data = pd.read_json("assets/Geo_interpolated_by_year.json")
with open("assets/laender_999_geo.json", "r", encoding="utf-8") as file:
    geojson_data = json.load(file)
years = [2006,2012,2016,2022]
regions = data['region'].unique()

trend_data = pd.read_json("assets/volunteering_time_series_fake.json")  

motiv_barrier_df = pd.read_json("assets/motivations_barriers_fake_data.json")

with open("assets/formal_volunteering_fake_data.json", "r", encoding="utf-8") as f:
    formal_data_by_year = json.load(f)

with open("assets/informal_volunteering_fake_data.json", "r", encoding="utf-8") as f:
    informal_data_by_year = json.load(f)


with open("assets/gender_comparison_data_multiyear.json", "r", encoding="utf-8") as f:
    gender_data_by_year = json.load(f)

with open("assets/errorBars_data_multiyear.json", "r", encoding="utf-8") as f:
    errorBars_data_by_year = json.load(f)



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    # General page title
    html.H1("Statistics of volunteering in Austria", className="text-center my-4 fw-bold"),
    # Top-left Menu Button + collabsable Sidebar
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
                    dbc.NavLink("Time-Series Trends (demgraphic comparison)", href="#timeseries-card", external_link=True),
                    dbc.NavLink("Time-Series Trends (volunteering type comparison", href="#ts2-time-series-card", external_link=True),
                    dbc.NavLink("Motivations and Barriers to Volunteering", href="#motivation-barrier-card", external_link=True),
                    dbc.NavLink("Volunteer Activity by Demographic Group", href="#activity-bar-card", external_link=True),
                    dbc.NavLink("Gender comparison in Volunteering", href="#gender-comparison-card", external_link=True),
                    dbc.NavLink("Volunteer Time Distribution", href="#errorBar-card", external_link=True),
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

            # Filters in one row
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
                ], width=2),

                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="stat-type-radio",
                        options=[
                            {'label': 'Percentage', 'value': 'perc'},
                            {'label': 'Avg Hours/week', 'value': 'avg_hours'},
                            {'label': 'Median Hours', 'value': 'median_hours'}
                        ],
                        value='perc',
                        labelStyle={'marginRight': '15px'}
                    ),
                ], width=2, style={'paddingTop': 30}),

                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[
                            {"label": str(y), "value": y}
                            for y in years
                        ],
                        value=int(max(years)),
                        clearable=False
                    )


                ], width=2),
                
                dbc.Col([
                    dbc.Button("Reset to Austria", id="reset-button", color="primary", className="mt-3")
                ], width=2, style={'textAlign': 'right'}),
            ], className='mb-4', align="center",justify="center"),

            dbc.Row([
                dbc.Col(dcc.Graph(id='austria-map'), width=6),
                dbc.Col(dcc.Graph(id='region-boxplot'), width=6)
            ]),
            dbc.Row([
                dbc.Col(html.Div(id='data-insights', className='data-insights'), width=12)
            ]),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),
                    html.P("The above graph shows the distribution of volunteers across Austrian regions.The percentages represent the proportion of people who have participated in the selected volunteering type during the selected year from the total population above 15 years old from the selected region.")
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )

        ])
    ],id="choropleth-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),
    # ... your existing layout above ...

    # ---- Time Series Card ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Time-series trends of Volunteering across demographic categories", className="mb-4 mt-2 text-center fw-semibold"),
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
                ], width=2),                
                dbc.Col([
                    html.Label("Demographic", className="mb-1"),
                    dcc.Dropdown(
                        id="ts-demographic-dropdown",
                        options=[{'label': d.capitalize().replace("_", " "), 'value': d}
                                for d in sorted(trend_data['demographic'].unique())],
                        value='age',  # Set your preferred default
                        clearable=False
                    )
                ], width=2),
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
            ], className='mb-4', align="center",justify="center"),
            dcc.Graph(id="ts-line-graph"),
            dbc.Alert(
                [   
                    html.H6("Graph description", className="alert-heading"),
                    html.P([
                        "The above graph shows the time series trends of volunteering across different demographic categories through the years. ",
                        "For the volunteering types (Any, Formal, Informal), the percentages represent the proportion of people who have participated in the selected volunteering type during the selected year from the number of residents in Austria who belong to the selected demographic category.",
                        html.Br(), html.Br(),
                        "However, for the volunteering types (Formal and Informal, Formal Only, Informal Only), the percentage is from the number of people from the selected demographic category who actually volunteered during the selected year.",
                        html.Br(), html.Br(),
                        "For instance:",
                        html.Br(),
                        "• Volunteering type = Formal, demographic = gender, statistic = percentage → percentage of men who did formal volunteering from all men in Austria.",
                        html.Br(),
                        "• Volunteering type = Formal only, demographic = gender, statistic = percentage → percentage of men who only did formal volunteering from all volunteering men in Austria."
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )            
        ])

    ],id="timeseries-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),

    # ---- Time Series Comparison by Volunteering Type ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Time-series trends of Volunteering across volunteering types", className="mb-4 mt-2 text-center fw-semibold"),

            dbc.Row([
                dbc.Col([
                    html.Label("Demographic Dimension", className="mb-1"),
                    dcc.Dropdown(
                        id="ts2-demographic-dropdown",
                        options=[
                            {"label": d.capitalize().replace("_", " "), "value": d}
                            for d in sorted(trend_data["demographic"].unique())
                        ],
                        value=sorted(trend_data["demographic"].unique())[0],
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Demographic Category", className="mb-1"),
                    dcc.Dropdown(
                        id="ts2-category-dropdown",
                        options=[],  # will be populated via callback
                        value=None,
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="ts2-radio",
                        options=[
                            {"label": "Percentage", "value": "perc"},
                            {"label": "Count", "value": "count"}
                        ],
                        value="perc",
                        labelStyle={"margin-right": "15px"}
                    )
                ], width=2, style={'paddingTop': 8}),

                dbc.Col([
                    html.Label("Year Range", className="mb-1"),
                    dcc.RangeSlider(
                        id="ts2-year-slider",
                        min=int(trend_data["year"].min()),
                        max=int(trend_data["year"].max()),
                        value=[
                            int(trend_data["year"].min()),
                            int(trend_data["year"].max())
                        ],
                        marks={
                            int(y): str(int(y)) for y in sorted(trend_data["year"].unique())
                        },
                        step=None
                    )
                ], width=4, style={'paddingTop': 12})
            ], align= "center",justify="center",className='mb-4'),


            dcc.Graph(id="ts2-line-graph"),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),                    
                    html.P([
                        "The above graph shows the time series trends of volunteering across different voluntering types through the years. ",
                        "For the volunteering types (Any, Formal, Informal), the percentages represent the proportion of people who have participated in the selected volunteering type during the selected year from the number of residents in Austria who belong to the selected demographic category.",
                        html.Br(), html.Br(),
                        "However, for the volunteering types (Formal and Informal, Formal Only, Informal Only), the percentage is from the number of people from the selected demographic category who actually volunteered during the selected year."
 
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )                        

        ])
    ], id="ts2-time-series-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),


    # ---- Diverging Bar Chart Card ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Motivations and Barriers to Volunteering", className="mb-4 mt-2 text-center fw-semibold"),
            dbc.Row([
                dbc.Col([
                    html.Label("Type", className="mb-1"),
                    dcc.RadioItems(
                        id="mb-type-radio",
                        options=[
                            {'label': 'Motivations', 'value': 'motivation'},
                            {'label': 'Barriers', 'value': 'barrier'}
                        ],
                        value='motivation',
                        labelStyle={'marginRight': '15px'}
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Gender", className="mb-1"),
                    dcc.Dropdown(
                        id="mb-gender-dropdown",
                        options=[{'label': g.capitalize(), 'value': g} for g in motiv_barrier_df['gender'].unique()],
                        value='all',
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Dropdown(
                        id="mb-year-dropdown",
                        options=[
                            {"label": str(y), "value": y} for y in years
                        ],
                        value=max(years),
                        clearable=False
                    )

                ], width=2)
            ], align="center", justify="center",className='mb-4'),

            dcc.Graph(id="mb-diverging-bar"),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),                    
                    html.P([
                        "The above graph shows the reasons that motivated people who volunteered in the selected year and the barriers that faced people who did not volunteer in the selected year, sorted by 'strongly agree'." 
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )                        
        ])
    ], id="motivation-barrier-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),

    # --- Stacked Bar Chart Card ---
    dbc.Card([
        dbc.CardBody([
            html.H4("Volunteer Activity by Demographic Group", className="mb-4 mt-2 text-center fw-semibold"),

            dbc.Row([
                dbc.Col([
                    html.Label("Type of Volunteering", className="mb-1"),
                    dcc.Dropdown(
                        id="activity-type-dropdown",
                        options=[
                            {"label": "Formal", "value": "formal"},
                            {"label": "Informal", "value": "informal"}
                        ],
                        value="formal",
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Demographic", className="mb-1"),
                    dcc.Dropdown(
                        id="activity-demographic-dropdown",
                        options=[
                            {"label": "Total", "value": "Total"},
                            {"label": "Gender", "value": "Gender"},
                            {"label": "Education", "value": "Education"},
                            {"label": "Frequency of Volunteering", "value": "Freq_of_volunteering"},
                            {"label": "Age", "value": "Age"},
                        ],
                        value="Gender",
                        clearable=False
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="activity-display-mode",
                        options=[
                            {"label": "Percentage", "value": "percent"},                            
                            {"label": "Count", "value": "count"}
                        ],
                        value="percent",
                        labelStyle={ 'marginRight': '15px'}
                    )
                ], width=2),
                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Dropdown(
                        id="activity-year-dropdown",
                        options=[
                            {"label": str(y), "value": y} for y in years
                        ],
                        value=max(years),
                        clearable=False
                    )

                ],width=2)

            ], align="center", justify="center",className='mb-4'),
            
            dcc.Graph(id="activity-stacked-bar"),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),                    
                    html.P([
                        "The above graph shows the distribution of formal / informal volunteers across volunteering activities.", 
                        html.Br(), html.Br(),
                        "i.e, each bar shows the percentage of voluneers who do each activity from all volunteers who do the selected volunteering type in the selected year, and filtering by demagrahpics divides these percentages further by demographic categories." 
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )                        
        ])
    ], id="activity-bar-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),

    # ---- Gender Comparison Card ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Gender Comparison in Volunteering", className="mb-4 mt-2 text-center fw-semibold"),

            dbc.Row([
                dbc.Col([
                    html.Label("Type of Volunteering", className="mb-1"),
                    dcc.Dropdown(
                        id="gender-type-dropdown",
                        options=[
                            {"label": "Formal", "value": "Formal"},
                            {"label": "Informal", "value": "Informal"}
                        ],
                        value="Formal",
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Dimension", className="mb-1"),
                        dcc.Dropdown(
                            id="gender-dimension-dropdown",
                            options=[],  # Initially empty
                            value=None,
                            clearable=False
                        )

                ], width=2),

                dbc.Col([
                    html.Label("Statistic", className="mb-1"),
                    dcc.RadioItems(
                        id="gender-display-mode",
                        options=[
                            {"label": "Percentage", "value": "percent"},                            
                            {"label": "Count", "value": "count"}

                        ],
                        value="percent",
                        labelStyle={ 'marginRight': '15px'}
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Dropdown(
                        id="gender-year-dropdown",
                        options=[
                            {"label": str(y), "value": y} for y in years
                        ],
                        value=max(years),
                        clearable=False
                    )

                ], width=2)
            ], align="center", justify="center",className='mb-4'),

            dcc.Graph(id="gender-comparison-bar"),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),                    
                    html.P([
                        "The above graph compares the contribution of men vs women in volunteering.", 
                        html.Br(),
                        "The bars show the percentage of contribution of each gender from all volunteers in the selected year, type of volunteering, and dimension category "
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )                  
      
        ])
    ], id="gender-comparison-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),
    # ---- Boxplot Card ----
    dbc.Card([
        dbc.CardBody([
            html.H4("Volunteer Time Distribution", className="mb-4 mt-2 text-center fw-semibold"),

            dbc.Row([
                dbc.Col([
                    html.Label("Type of Volunteering", className="mb-1"),
                    dcc.Dropdown(
                        id="errorBar-voltype-dropdown",
                        options=[
                            {"label": "Any", "value": "Total"},
                            {"label": "Formal", "value": "Formal"},
                            {"label": "Informal", "value": "Informal"}
                        ],
                        value="Total",
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Demographic", className="mb-1"),
                    dcc.Dropdown(
                        id="errorBar-demographic-dropdown",
                        options=[
                            {"label": "Total", "value": "Total"},
                            {"label": "Gender", "value": "Gender"},
                            {"label": "Age", "value": "Age"},
                            {"label": "Education", "value": "Education"},
                            {"label": "Migration Background", "value": "MigrationBackground"},
                            {"label": "Employment", "value": "Employment"},
                            {"label": "Municipality Size", "value": "MunicipalitySize"},
                            {"label": "Region", "value": "Region"},
                            {"label": "Task Type", "value": "TaskType"}
                        ],
                        value="Total",
                        clearable=False
                    )
                ], width=2),

                dbc.Col([
                    html.Label("Year", className="mb-1"),
                    dcc.Dropdown(
                        id="errorBar-year-dropdown",
                        options=[
                            {"label": str(y), "value": y} for y in years
                        ],
                        value=max(years),
                        clearable=False
                    )
                ], width=2)
            ], align="center", justify="center",className='mb-4'),

            dcc.Graph(id="errorBar-figure"),
            dbc.Alert(
                [
                    html.H6("Graph description", className="alert-heading"),                    
                    html.P([
                        "The above graph compares weekly time spent on different volunteering types by each demographic category.The height of each bar indicates the median volunteering time, while the black diamond marker shows the mean (average) value. The error bars extending from the diamond represent the interquartile range, capturing the spread between the 25th and 75th percentiles. ", 
                        #html.Br(),
                        
                    ])                                               
                ],
                color="light",
                style={"border": "1px solid #ccc", "marginTop": "10px"}
            )
        ])
    ], id="errorBar-card", className="mb-5 shadow-sm border-0",style={"backgroundColor": "#f8f9fa"}),





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



import plotly.graph_objects as go

@app.callback(
    Output('region-boxplot', 'figure'),
    Output('austria-map', 'figure'),
    Output('selected-region', 'data'),
    Input('austria-map', 'clickData'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value'),
    Input('year-dropdown', 'value'),
    Input('reset-button', 'n_clicks'),
    State('selected-region', 'data'),
    prevent_initial_call=False
)
def update_visuals(click_data, metric_value, stat_type, year, reset_clicks, current_region):
    triggered = ctx.triggered_id

    if triggered == "reset-button":
        new_region = "Austria"
    elif triggered == "austria-map" and click_data and click_data.get('points') and 'location' in click_data['points'][0]:
        new_region = click_data['points'][0]['location']
    elif current_region in regions:
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

    # Error bar chart (replaces boxplot)
    if new_region not in d_year['region'].values:
        new_region = "Austria"

    q1 = d_year.loc[d_year['region'] == new_region, f'25_hrs_{prefix}'].values[0]
    median = d_year.loc[d_year['region'] == new_region, f'median_hours_{prefix}'].values[0]
    q3 = d_year.loc[d_year['region'] == new_region, f'75_hrs_{prefix}'].values[0]
    avg = d_year.loc[d_year['region'] == new_region, f'avg_hours_{prefix}'].values[0]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[new_region],
        y=[median],
        error_y=dict(
            type="data",
            symmetric=False,
            array=[q3 - median],
            arrayminus=[median - q1],
            color="black",
            thickness=2,
            width=8
        ),
        marker_color="steelblue",
        name="Median with IQR",
        hovertemplate=(
            f"<b>{new_region}</b><br>"
            f"Q3 (75th %): {q3}<br>"
            f"Median (50th %): {median}<br>"
            f"Q1 (25th %): {q1}<extra></extra>"
        )
    ))

    fig.add_trace(go.Scatter(
        x=[new_region],
        y=[avg],
        mode="markers",
        marker=dict(
            color="black",
            size=10,
            symbol="diamond"
        ),
        name="Average",
        hovertemplate=(
            f"<b>{new_region}</b><br>"
            f"Average Hours: {avg}<extra></extra>"
        )
    ))

    fig.update_layout(
        title=f"Volunteer Hours – {new_region} ({year})",
        yaxis_title="Hours per Week",
        xaxis_title="",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05
        )
    )

    # --- Choropleth map as in your current code ---
    column = resolve_column(metric_value, stat_type)
    value = d_year.loc[d_year['region'] == new_region, column].values[0]

    # Determine unit for labeling
    label_map = {
        'perc': '%',
        'avg_hours': 'hrs',
        'median_hours': 'hrs'
    }
    unit = label_map.get(stat_type, '')

    fig_map = px.choropleth(
        d_year,
        locations="region",
        geojson=geojson_data,
        color=column,
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        title=f"{new_region} {value:.1f}{unit} ({year})"
    )

    if new_region != 'Austria':
        selected_feature = next(
            (f for f in geojson_data['features'] if f['properties']['name'] == new_region),
            None
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

    return fig, fig_map, new_region


@app.callback(
    Output('data-insights', 'children'),
    Input('metric-dropdown', 'value'),
    Input('stat-type-radio', 'value'),
    Input('year-dropdown', 'value')
,
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
        #html.H4(f"Year: {year}"),
        html.H5(f"Highest: {highest['region']} ({highest[column]} {label_map[stat_type_value]})"),
        html.H5(f"Lowest: {lowest['region']} ({lowest[column]} {label_map[stat_type_value]})")
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
            y_label = "Number of Volunteers (thousands)"
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


@app.callback(
    Output("mb-diverging-bar", "figure"),
    Input("mb-type-radio", "value"),
    Input("mb-gender-dropdown", "value"),
    Input("mb-year-dropdown", "value")
)
def update_motiv_barrier_chart(type_choice, gender_choice, selected_year):
    df = motiv_barrier_df[
        (motiv_barrier_df['type'] == type_choice) &
        (motiv_barrier_df['gender'] == gender_choice) &
        (motiv_barrier_df['year'] == selected_year)
    ].sort_values("fully_agree", ascending=True)

    categories = df['category']

    import plotly.graph_objects as go
    fig = go.Figure()

    fig.add_bar(
        x=-df['rather_disagree'],
        y=categories,
        orientation='h',
        name='Rather disagree',
        marker_color='#ff9896'
    )

    fig.add_bar(
        x=-df['not_at_all'],
        y=categories,
        orientation='h',
        name='Not at all',
        marker_color='#d62728'
    )

    fig.add_bar(
        x=df['rather_agree'],
        y=categories,
        orientation='h',
        name='Rather agree',
        marker_color='#98df8a'
    )
    fig.add_bar(
        x=df['fully_agree'],
        y=categories,
        orientation='h',
        name='Fully agree',
        marker_color='#2ca02c'
    )

    fig.update_layout(
        barmode='relative',
        title=f"{type_choice.capitalize()} – {gender_choice.capitalize()} ({selected_year})",
        xaxis_title="Level of Agreement (%)",
        yaxis_title="",
        legend_title="Agreement Level",
        xaxis=dict(
            tickmode='array',
            tickvals=[-100,-80, -60, -40, -20, 0, 20, 40, 60, 80,100],
            ticktext=[str(abs(v)) for v in [-100,-80, -60, -40, -20, 0, 20, 40, 60, 80,100]]
        ),
        height=600,
        template='plotly_white'
    )

    return fig


@app.callback(
    Output("activity-stacked-bar", "figure"),
    Input("activity-type-dropdown", "value"),
    Input("activity-demographic-dropdown", "value"),
    Input("activity-display-mode", "value"),
    Input("activity-year-dropdown", "value")
)
def update_activity_stacked_bar(vol_type, selected_demo, display_mode,selected_year):



    # Choose dataset

    data_by_year = formal_data_by_year if vol_type == "formal" else informal_data_by_year
    year_str = str(selected_year)

    if year_str in data_by_year:
        data_source = data_by_year[year_str]
    else:
        # Fallback to empty data if year missing
        return px.bar(title="No data available for selected year")

    if selected_demo not in data_source:
        return px.bar(title="No data available for selected demographic")

    df = pd.DataFrame(data_source[selected_demo])


    # Extract total volunteers from "Total"
    total_list = data_source["Total"]
    all_volunteers = next((item["all_volunteers"] for item in total_list if "all_volunteers" in item), None)

    # Calculate display value
    if display_mode == "percent" and all_volunteers:
        df["value"] = df["count"] / all_volunteers * 100
        y_axis_title = "Percentage of Volunteers (%)"
    else:
        df["value"] = df["count"]
        y_axis_title = "Number of Volunteers (thousands)"

    # Plot
    if selected_demo == "Total":
        df = df[df["name"].notnull()]
        fig = px.bar(
            df,
            x="name",
            y="value",
            labels={"name": "Activity", "value": y_axis_title},
            title=f"{vol_type.capitalize()} Volunteering - Total"
        )
    else:
        fig = px.bar(
            df,
            x="name",
            y="value",
            color="category",
            labels={"name": "Activity", "value": y_axis_title, "category": selected_demo},
            title=f"{vol_type.capitalize()} Volunteering by {selected_demo} ({selected_year})"

        )

    fig.update_layout(
        barmode="stack",
        xaxis_tickangle=-45,
        template="plotly_white",
        height=500
    )
    return fig


@app.callback(
    Output("gender-comparison-bar", "figure"),
    Input("gender-type-dropdown", "value"),
    Input("gender-dimension-dropdown", "value"),
    Input("gender-display-mode", "value"),
    Input("gender-year-dropdown", "value")
)
def update_gender_comparison(vol_type, dimension, display_mode, selected_year):
    import plotly.express as px
    import pandas as pd

    # Load data for the chosen year
    year_data = gender_data_by_year.get(str(selected_year), {})

    # Compose key for this dimension
    key = f"{vol_type}_{dimension}"
    section = year_data.get(key)

    if section is None:
        return px.bar(title="No data for selected filters.")

    df = pd.DataFrame(section)

    # Determine x-axis label based on dimension
    if dimension == "NumberOfOrgs":
        x_col = "num_orgs"
    elif dimension == "TaskTypes":
        x_col = "task"
    elif dimension == "Areas":
        x_col = "area"
    elif dimension == "Time/week":
        x_col = "hours_range/week"
    else:
        x_col = "category"

    if display_mode == "count":
        df_long = pd.melt(
            df,
            id_vars=[x_col],
            value_vars=["men_count", "women_count"],
            var_name="Gender",
            value_name="Value"
        )
        y_label = "Number of Volunteers (thousands)"
    else:
        df_long = pd.melt(
            df,
            id_vars=[x_col],
            value_vars=["men_perc", "women_perc"],
            var_name="Gender",
            value_name="Value"
        )
        y_label = "Percentage of Volunteers (%)"

    # Map gender names
    df_long["Gender"] = df_long["Gender"].replace({
        "men_count": "Men",
        "women_count": "Women",
        "men_perc": "Men",
        "women_perc": "Women"
    })

    # Plot grouped bar
    fig = px.bar(
        df_long,
        x=x_col,
        y="Value",
        color="Gender",
        barmode="group",
        color_discrete_map={
            "Men": "blue",
            "Women": "red"
        }
    )

    fig.update_layout(
        title=f"{vol_type} Volunteering – {dimension} ({selected_year})",
        yaxis_title=y_label,
        xaxis_title=x_col,
        template="plotly_white",
        height=500
    )

    return fig

@app.callback(
    Output("gender-dimension-dropdown", "options"),
    Output("gender-dimension-dropdown", "value"),
    Input("gender-type-dropdown", "value")
)
def update_dimension_options(vol_type):
    if vol_type == "Formal":
        options = [
            {"label": "Number of Organizations", "value": "NumberOfOrgs"},
            {"label": "Task Types", "value": "TaskTypes"},
            {"label": "Areas", "value": "Areas"},
            {"label": "Time/week", "value": "Time/week"}
        ]
        default_value = "Areas"
    else:
        options = [
            {"label": "Areas", "value": "Areas"},
            {"label": "Time/week", "value": "Time/week"}
        ]
        default_value = "Areas"
    return options, default_value

@app.callback(
    Output("errorBar-figure", "figure"),
    Input("errorBar-voltype-dropdown", "value"),
    Input("errorBar-demographic-dropdown", "value"),
    Input("errorBar-year-dropdown", "value"),
)
def update_errorBar(vol_type, demographic, selected_year):
    import plotly.graph_objects as go
    import plotly.colors as pc

    # Retrieve year data
    year_data = errorBars_data_by_year.get(str(selected_year), {})
    category_data = year_data.get(demographic, [])

    # Filter by volunteering type
    df = pd.DataFrame([
        d for d in category_data
        if d["volunteering_type"] == vol_type
    ])

    if df.empty:
        return go.Figure().update_layout(
            title=f"No data for selection in {selected_year}"
        )

    # Prepare color palette
    color_list = pc.qualitative.Plotly
    colors = color_list * (len(df) // len(color_list) + 1)

    fig = go.Figure()

    for i, (_, row) in enumerate(df.iterrows()):
        # Add bar for median with IQR as error bars
        fig.add_trace(go.Bar(
            x=[row["category_value"]],
            y=[row["percentile_50"]],
            error_y=dict(
                type="data",
                symmetric=False,
                array=[row["percentile_75"] - row["percentile_50"]],
                arrayminus=[row["percentile_50"] - row["percentile_25"]],
                thickness=2,
                width=8,
                color="rgba(0,0,0,0.5)"
            ),
            name=row["category_value"],
            marker_color=colors[i],
            hovertemplate=(
                f"<b>{row['category_value']}</b><br>"
                f"Q3 (75th %): {row['percentile_75']}<br>"
                f"Median (50th %): {row['percentile_50']}<br>"
                f"Q1 (25th %): {row['percentile_25']}<br>"
                
            )
        ))

        # Add mean as a scatter point overlaying the bar
        fig.add_trace(go.Scatter(
            x=[row["category_value"]],
            y=[row["avg_hours"]],
            mode="markers",
            marker=dict(
                color="black",
                size=10,
                symbol="diamond"
            ),
            name=f"Mean ({row['category_value']})",
            hovertemplate=(
                f"<b>{row['category_value']}</b><br>"
                f"Mean: {row['avg_hours']}<extra></extra>"
            ),
            showlegend=True
        ))

    fig.update_layout(
        title=f"Volunteer Hours per Week – {vol_type} – {demographic} ({selected_year})",
        yaxis_title="Hours per Week",
        xaxis_title=demographic if demographic != "Total" else "",
        barmode="group",
        template="plotly_white",
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05,
            title="Legend"
        )
    )

    return fig

@app.callback(
    Output("ts2-category-dropdown", "options"),
    Output("ts2-category-dropdown", "value"),
    Input("ts2-demographic-dropdown", "value")
)
def update_ts2_categories(demographic):
    if demographic is None:
        return [], None

    filtered = trend_data[trend_data["demographic"] == demographic]
    unique_categories = sorted(filtered["category"].unique())

    options = [
        {"label": cat, "value": cat} for cat in unique_categories
    ]

    # Default to first category
    default_value = unique_categories[0] if unique_categories else None

    return options, default_value

@app.callback(
    Output("ts2-line-graph", "figure"),
    Input("ts2-demographic-dropdown", "value"),
    Input("ts2-category-dropdown", "value"),
    Input("ts2-radio", "value"),
    Input("ts2-year-slider", "value")
)
def update_ts2_graph(demographic, category, display_mode, year_range):
    import plotly.express as px

    if demographic is None or category is None:
        return px.line(title="No data available.")

    # Filter the trend data
    df_filtered = trend_data[
        (trend_data["demographic"] == demographic) &
        (trend_data["category"] == category) &
        (trend_data["year"] >= year_range[0]) &
        (trend_data["year"] <= year_range[1])
    ]

    # Volunteering types to compare
    vol_types = [
        "any",
        "formal",
        "informal",
        "both_formal_and_informal",
        "formal_only",
        "informal_only"
    ]

    fig = px.line()

    for vol_type in vol_types:
        if display_mode == "perc":
            y_col = f"{vol_type}_volunteer_perc"
            y_label = "Percentage of Volunteers"
        else:
            y_col = f"{vol_type}_volunteer_count"
            y_label = "Number of Volunteers (thousands)"

        if y_col in df_filtered.columns:
            fig.add_scatter(
                x=df_filtered["year"],
                y=df_filtered[y_col],
                mode='lines+markers',
                name=vol_type.replace("_", " ").capitalize()
            )

    fig.update_layout(
        title=f"Volunteering Type Comparison – {category} ({demographic.capitalize()})",
        xaxis_title="Year",
        yaxis_title=y_label,
        legend_title="Type of Volunteering",
        height=500,
        template="plotly_white"
    )

    return fig



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)