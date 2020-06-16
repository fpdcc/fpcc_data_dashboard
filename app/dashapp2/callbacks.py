from dash.dependencies import Input
from dash.dependencies import Output
from .layout import *

def gj_query(table):
    """queries tables and returns json to build geojson"""
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        with connection:
            with cur:
                query = """SELECT jsonb_build_object('type','FeatureCollection','features', jsonb_agg(feature)) FROM (SELECT jsonb_build_object('type','Feature','id', buildings_id,'geometry',ST_AsGeoJSON(st_transform(geom, 4326))::jsonb,'properties',to_jsonb(inputs) - 'geom') AS feature FROM (SELECT buildings_id, geom FROM {} where demolished <> 'yes') inputs) features;""".format(table).replace('\n',' ')

                cur.execute(query)
                geoj = cur.fetchall()
                return geoj

    finally:
        connection.close()

def output_geojson(jsn):
    """outputs a tuple from gj_query().
    To get geojson for map use output_geojson()[0],
    To get dict for the map df use output_geojson()[1]."""
    geoj = jsn[0]
    geoj2 = json.dumps(geoj)
    geoj3 = geojson.loads(geoj2)
    return (geoj3, geoj)

def create_map(dataf, geoj):
    """create map with a dataframe and geoJson then update layout"""
    fig = px.choropleth_mapbox(dataf,
                                geojson=geoj,
                                locations="buildings_id",
                                featureidkey="properties.buildings_id",
                                #color='district',
                                opacity=0.5,
                               )
    fig.update_layout(
                        mapbox_style="carto-positron",
                        mapbox_zoom=8,
                        mapbox_center = {"lat": 41.8, "lon": -87.8},
                        margin={"r":15,"t":15,"l":15,"b":15},
                        showlegend=False
                     )
    fig.update_geos(fitbounds="locations")
    return fig

def table_query(table):
    """sql query for DataTable"""
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        table_data = pd.read_sql_query("select * from {} where demolished <> 'yes'".format(table),con=connection)
        return table_data
    finally:
        connection.close()

def bldg_proj_query(table):
    """sql query for DataTable"""
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        table_data = pd.read_sql_query("select * from {} where complete = 0".format(table),con=connection)
        return table_data
    finally:
        connection.close()

def summary_card_content(df):
    """return summary for all uncompleted priority classes"""
    priority_class = list(df.groupby(['priority_class']).groups.keys())
    priority_card_content = {}
    for p in priority_class:
        total_projects = len(df.groupby(['priority_class']).groups[p])
        priority_card_content[p] = total_projects
    return priority_card_content

BUILDINGS_GEODATA = 'quercus.buildings'
BUILDINGS_PROJECTS = 'catalpa.building_projects'

### home tab ###
priority_card_content = [
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text",
            ),
        ]
    ),
]

df = pd.DataFrame(
            {
        "Project ID": [1, 2, 3, 4],
        "Location": ["Miller Meadow", "Dan Ryan", "Sand Ridge", "Bunker Hill"],
        "Building Name": ["Building 1", "Building 2", "Building 3", "Building 4"],
            }
        )

data = px.data.gapminder()
data_canada = data[data.country == 'Canada']

### general tab ###
# DataTable
building_table_df = table_query(BUILDINGS_GEODATA)

# building geojson
building_gj = output_geojson(gj_query(BUILDINGS_GEODATA)[0])[0]

# building dataframe
building_df = json_normalize(output_geojson(gj_query(BUILDINGS_GEODATA)[0])[1]['features'])
building_df = pd.DataFrame(building_df.drop(columns=['geometry.coordinates', 'geometry.type', 'type']))
building_df = building_df.rename(columns={'properties.buildings_id': 'buildings_id'})

### details tab ###
card_content_bldg_detail = [
    dbc.CardHeader("Card header"),
    dbc.CardBody([
            html.H5("Card title", className="card-title"),
            html.P(
                "This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.This is some card content that we'll reuse.",
                className="card-text",
            ),
        ]),
]

card_content_bldg_docs = [
    dbc.Card([
        dbc.CardHeader("Card header"),
        dbc.CardImg(src="https://fpdccfilestore.nyc3.digitaloceanspaces.com/danryan_visitorcenter.jpg", top=True),
        dbc.CardBody([
                html.H5("Card title", className="card-title"),
                html.P(
                    "This is some card content that we'll reuse.This is some card content that we'll reuse.",
                    className="card-text",
                    ),
                dbc.CardLink("Card link", href="#"),
                dbc.CardLink("External link", href="https://google.com"),
            ]),
        ]),
]


def register_callbacks(dashapp):
    @dashapp.callback(Output("content", "children"), [Input("tabs", "active_tab")])
    def switch_tab(at):
        if at == "home":

            home_tab_content = [
                html.Div(
                # cards
                    dbc.Row(
                        [
                            dbc.Col(dbc.Card(dbc.CardBody(
                                    [
                                        html.H5("Priority Class 1", className="card-title"),
                                        html.P(
                                            "Total projects: 18 | Total Cost:999",
                                            className="card-text",
                                        ),
                                    ]
                                ), color="primary", inverse=True)),
                            dbc.Col(dbc.Card(dbc.CardBody(
                                    [
                                        html.H5("Priority Class 2", className="card-title"),
                                        html.P(
                                            "Total projects: 290 | Total Cost:999",
                                            className="card-text",
                                        ),
                                    ]
                                ), color="primary", inverse=True)),
                            dbc.Col(dbc.Card(dbc.CardBody(
                                    [
                                        html.H5("Priority Class 3", className="card-title"),
                                        html.P(
                                            "Total projects: 999 | Total Cost:999",
                                            className="card-text",
                                        ),
                                    ]
                                ), color="info", inverse=True)),
                            dbc.Col(dbc.Card(dbc.CardBody(
                                    [
                                        html.H5("Priority Class 4", className="card-title"),
                                        html.P(
                                            "Total projects: 283 | Total Cost:999",
                                            className="card-text",
                                        ),
                                    ]
                                ), color="info", inverse=True)),
                        ],
                        className="my-4",
                            ),
                        ),
                # tables
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.H4(children="Buildings Above Replacement Cost"),
                                dbc.Table.from_dataframe(
                                    df,
                                    bordered=True,
                                    dark=True,
                                    hover=True,
                                    responsive=True,
                                    striped=True,)
                                ]),md=6,
                            ),
                        dbc.Col(
                            html.Div([
                                html.H4(children="Building Asset End of Useful Life"),
                                dbc.Table.from_dataframe(
                                    df,
                                    bordered=True,
                                    dark=True,
                                    hover=True,
                                    responsive=True,
                                    striped=True,)
                                ]),md=6,
                            ),
                        ], justify='center'),
                # bar graph
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                dcc.Graph(
                                    figure = px.bar(
                                        data_canada,
                                        x='year',
                                        y='pop',
                                        hover_data=['lifeExp', 'gdpPercap'], color='lifeExp',
                                        labels={'pop':'population of Canada'},
                                        )
                                    )
                                )
                            )
                        ),
                # footer
                    dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']})),


                ]
            return home_tab_content




        elif at == "general":

            general_tab_content = [
# Row for dropdown menus
                    dbc.Row([
                            dbc.Col(
                                html.Div(
                                    dcc.Dropdown(
                                        id='zone',
                                        value = 0,
                                        placeholder="Zone",
                                        #options=[{'label':ns, 'value':ns} for ns in sd_list['district']],
                                        multi=True
                                        ),className="my-4"
                                    ),md=3
                                ),
                            dbc.Col(
                                html.Div(
                                    dcc.Dropdown(
                                        id='comm_dist',
                                        value = 0,
                                        placeholder="Commissioner District",
                                        #options=[{'label':ns, 'value':ns} for ns in hd_list['district']],
                                        multi=True
                                        ),className="my-4"
                                    ),md=3
                                ),
                            dbc.Col(
                                html.Div(
                                    dcc.Dropdown(
                                        id='year_built',
                                        value = 0,
                                        placeholder="Year Built",
                                        #options=[{'label':ns, 'value':ns} for ns in cd_list['district']],
                                        multi=True
                                        ),className="my-4"
                                    ),md=3
                                ),
                            dbc.Col(
                                html.Div(
                                    dcc.Dropdown(
                                        id='priority',
                                        value = 0,
                                        placeholder="Priority",
                                        #options=[{'label':ns, 'value':ns} for ns in cd_list['district']],
                                        multi=True
                                        ),className="my-4"
                                    ),md=3
                             ),

                        ], justify='center', id='filter_bldg_dropdowns'),
# Row for map
                    dbc.Row([
                           dbc.Col(
                               html.Div([
                                       dbc.Spinner(color="primary", size='lg',
                                           children=[
                                                dcc.Graph(
                                                       id = 'building_map',
                                                       figure = create_map(building_df, building_gj)
                                                    )
                                                   ]),
                                       ]),
                               ),
                        ]),
# Data table
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                dash_table.DataTable(
                                            id='building-table',
                                            export_format='xlsx',
                                            data=building_table_df.to_dict('records'),
                                            columns=[
                                                    {"name": "Buildings Id",
                                                    "id": "buildings_id"},
                                                    {"name": "Building Name",
                                                    "id": "building_name"},
                                                    {"name": "Current Address",
                                                    "id": "address_current"},
                                                    {"name": "Building Type",
                                                    "id": "building_type"},
                                                    {"name": "Improvement Year",
                                                    "id": "improvement_year"},
                                                    ],
                                            merge_duplicate_headers=True,
                                            style_as_list_view=True,
                                            # fixed_rows={ 'headers': True, 'data': 0 },
                                            editable=False,
                                            filter_action="native",
                                            sort_action="native",
                                            sort_mode='multi',
                                            row_selectable='multi',
                                            row_deletable=False,
                                            selected_rows=[],
                                            page_action='native',
                                            page_current= 0,
                                            page_size= 10,
                                            style_cell={
                                                'textAlign': 'left',
                                                'padding': '5px',
                                                'height': 'auto',
                                                #'minWidth': '55px',
                                                'maxWidth': '100px',
                                                'whiteSpace': 'normal',
                                                'color': theme_colors['cell_color']
                                                },
                                            style_data={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                                'lineHeight': '17px'
                                                },
                                            style_data_conditional=[
                                                    {
                                                        'if': {'row_index': 'odd'},
                                                        'backgroundColor': theme_colors['table_background_color']
                                                    }
                                                ],
                                            #style_table={'maxHeight': '300px','overflowY': 'scroll'},
                                            # style_cell_conditional=[
                                            #     {
                                            #         'if': {'column_id': c},
                                            #         'textAlign': 'center'
                                            #     } for c in ['house_district', 'senate_district', 'commissioner_district']
                                            #     ],
                                            style_header={
                                                'textAlign': 'center',
                                                'fontWeight': 'bold',
                                                'color': 'white',
                                                'backgroundColor': theme_colors['table_header_color']
                                                },
                                        ),
                                    ), id='div_bldgtable',
                                )
                            ],id='row_bldgtable'),
# footer
                    dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']})),
            ]

            return general_tab_content

        elif at == "details":


            details_tab_content = [
# Row for dropdown menus
            dbc.Row([
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='zone',
                                value = 0,
                                placeholder="Zone",
                                #options=[{'label':ns, 'value':ns} for ns in sd_list['district']],
                                multi=True
                                ),className="my-4"
                            ),md=3
                        ),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='comm_dist',
                                value = 0,
                                placeholder="Commissioner District",
                                #options=[{'label':ns, 'value':ns} for ns in hd_list['district']],
                                multi=True
                                ),className="my-4"
                            ),md=3
                        ),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='year_built',
                                value = 0,
                                placeholder="Year Built",
                                #options=[{'label':ns, 'value':ns} for ns in cd_list['district']],
                                multi=True
                                ),className="my-4"
                            ),md=3
                        ),
                    dbc.Col(
                        html.Div(
                            dcc.Dropdown(
                                id='priority',
                                value = 0,
                                placeholder="Priority",
                                #options=[{'label':ns, 'value':ns} for ns in cd_list['district']],
                                multi=True
                                ),className="my-4"
                            ),md=3
                     ),

                ], justify='center', id='filter_bldgdetail_dropdowns'),
# Row for build select
            dbc.Row([
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='building_name',
                            value = 0,
                            placeholder="Building Name",
                            #options=[{'label':ns, 'value':ns} for ns in sd_list['district']],
                            multi=True
                            ),className="my-4"
                        ),md=12
                    ),
                ], justify='center', id='filter_bldgselect_dropdown'),
# building detail cards
            dbc.Row([
                    dbc.Col(html.Div(dbc.Card(card_content_bldg_detail, color="light")),md=6,className="mb-4"),
                    dbc.Col(html.Div(card_content_bldg_docs),md=6,className="mb-4"),
                ]),
# Data table
        dbc.Row([
            dbc.Col(
                html.Div(
                    dash_table.DataTable(
                                id='building-table',
                                export_format='xlsx',
                                data=building_table_df.to_dict('records'),
                                columns=[
                                        {"name": "Buildings Id",
                                        "id": "buildings_id"},
                                        {"name": "Building Name",
                                        "id": "building_name"},
                                        {"name": "Current Address",
                                        "id": "address_current"},
                                        {"name": "Building Type",
                                        "id": "building_type"},
                                        {"name": "Improvement Year",
                                        "id": "improvement_year"},
                                        ],
                                merge_duplicate_headers=True,
                                style_as_list_view=True,
                                # fixed_rows={ 'headers': True, 'data': 0 },
                                editable=False,
                                filter_action="native",
                                sort_action="native",
                                sort_mode='multi',
                                row_selectable='multi',
                                row_deletable=False,
                                selected_rows=[],
                                page_action='native',
                                page_current= 0,
                                page_size= 10,
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '5px',
                                    'height': 'auto',
                                    #'minWidth': '55px',
                                    'maxWidth': '100px',
                                    'whiteSpace': 'normal',
                                    'color': theme_colors['cell_color']
                                    },
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '17px'
                                    },
                                style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': theme_colors['table_background_color']
                                        }
                                    ],
                                #style_table={'maxHeight': '300px','overflowY': 'scroll'},
                                # style_cell_conditional=[
                                #     {
                                #         'if': {'column_id': c},
                                #         'textAlign': 'center'
                                #     } for c in ['house_district', 'senate_district', 'commissioner_district']
                                #     ],
                                style_header={
                                    'textAlign': 'center',
                                    'fontWeight': 'bold',
                                    'color': 'white',
                                    'backgroundColor': theme_colors['table_header_color']
                                    },
                            ),
                        ), id='div_bldgdetail_table',
                    )
                ],id='row_bldg_detail_table'),
# footer
            dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']})),
            ]
            return details_tab_content
