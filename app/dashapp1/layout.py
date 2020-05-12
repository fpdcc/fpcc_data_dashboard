# Imports
import sys, os
import dash
# from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import pandas as pd
import pandas.io.sql as psql
# import plotly.graph_objs as go
import plotly.express as px
import psycopg2 as pg
import numpy as np
#from .. import creds as creds
import json
from urllib.request import urlopen
from pandas.io.json import json_normalize
import geopandas as gpd
from pathlib import Path

basedir = Path(os.path.abspath(os.path.dirname(__file__))).parent
datadir = Path(basedir / 'assets')
POSTGRESQL = os.environ.get('POSTGRESQL')

# Load and preprocess data
# filename = os.path.join(app.instance_path, 'my_folder', 'my_file.txt')

#project data
# conn_string = "host="+ creds.PGHOST +" port="+ str(creds.PGPORT) +" dbname="+ creds.PGDATABASE +" user=" + creds.PGUSER +" password="+ creds.PGPASSWORD
conn_string=POSTGRESQL
connection=pg.connect(conn_string)

df = pd.read_sql_query('select * from public.fpcc_capital_needs_non_mft_21_24',con=connection)
df.set_index('id', inplace=True, drop=False)


# import commissioner district geoJson
# geojson must have id and district fields
comm_dist_file = datadir / "comm_dist_4326.geojson"
comm_dist_gj = gpd.read_file(comm_dist_file)
# with open('./comm_dist_4326.geojson') as response:
#    comm_dist_gj = json.load(response)

# create a comm dist df to display map
new_comm_dist = pd.DataFrame(comm_dist_gj.drop(columns='geometry'))
# new_comm_dist = json_normalize(comm_dist_gj['features'])
# new_comm_dist = new_comm_dist[['properties.ogc_fid', 'properties.district']]
new_comm_dist = new_comm_dist.rename(columns={'ogc_fid': 'id'})
cd_list = new_comm_dist.astype({'district': 'int32'}).sort_values('district')

# import senate geoJson
senate_file = datadir / 'senate_4326.geojson'
senate_gj = gpd.read_file(senate_file)
# with open('./senate_4326.geojson') as response:
#    senate_gj = json.load(response)

# create a senate dist df to display map
new_senate = pd.DataFrame(senate_gj.drop(columns='geometry'))
# new_senate = json_normalize(senate_gj['features'])
# new_senate = new_senate[['properties.id', 'properties.district']]
# new_senate = new_senate.rename(columns={'id': 'id','district': 'district'})
sd_list = new_senate.astype({'district': 'int32'}).sort_values('district')

#import house geoJson
house_file = datadir / 'house_4326.geojson'
house_gj = gpd.read_file(house_file)
# with open('./house_4326.geojson') as response:
#    house_gj = json.load(response)

# create a house dist df to display map
new_house = pd.DataFrame(house_gj.drop(columns='geometry'))
# new_house = json_normalize(house_gj['features'])
# new_house = new_house[['properties.id', 'properties.district']]
# new_house = new_house.rename(columns={'properties.id': 'id','properties.district': 'district'})
hd_list = new_house.astype({'district': 'int32'}).sort_values('district')

# selected_commdist_gj = comm_dist_gj.loc[comm_dist_gj['district'].isin(['1'])]
# selected_commdist_df = new_comm_dist.loc[new_comm_dist['district'] == '1']

theme_colors = []

#map setup
def create_map(dataf, geoj):
    # fig = go.Figure(
    #          go.Choroplethmapbox(
    #              geojson=geoj,
    #              locations=dataf.district,
    #              z=dataf.district,
    #              featureidkey="properties.district",
    #              colorscale="Viridis",
    #              zmin=0,
    #              zmax=12,
    #              marker_opacity=0.5,
    #              marker_line_width=0))

    fig = px.choropleth_mapbox(dataf,
                                geojson=geoj,
                                locations="district",
                                featureidkey="properties.district",
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

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("CIP", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Data Sets", header=True),
                dbc.DropdownMenuItem("Trails", href="#"),
                dbc.DropdownMenuItem("Parking Lots", href="#"),
                dbc.DropdownMenuItem("Picnic Groves", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="FPCC Data",
    brand_href="#",
    color="#015249",
    dark=True,
)

body = dbc.Container(
    children=[

# Row for dropdown menus
         dbc.Row([
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='senate_dropdown',
                            value = 0,
                            placeholder="Select Senate District",
                            options=[{'label':ns, 'value':ns} for ns in sd_list['district']],
                            multi=True
                            ),className="my-2"
                        ),md=4
                    ),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='house_dropdown',
                            value = 0,
                            placeholder="Select House District",
                            options=[{'label':ns, 'value':ns} for ns in hd_list['district']],
                            multi=True
                            ),className="my-2"
                        ),md=4
                    ),
                dbc.Col(
                    html.Div(
                        dcc.Dropdown(
                            id='commdist_dropdown',
                            value = 0,
                            placeholder="Select Commissioner District",
                            options=[{'label':ns, 'value':ns} for ns in cd_list['district']],
                            multi=True
                            ),className="my-2"
                        ),md=4
                 ),
            ], justify='center', id='dropdowns'),

# Row for maps
         dbc.Row([
                dbc.Col(
                    html.Div([
                            dbc.Spinner(color="primary", size='lg',
                                children=[dcc.Graph(
                                                id = 'senate_map',
                                                #figure = create_map(new_senate, senate_gj)
                                                    )
                                        ]),
                            ]),md=4, className="d-none d-sm-block" #removes map on small devices
                    ),
                dbc.Col(
                    html.Div([
                            dbc.Spinner(color="primary", size="lg",
                                children=[dcc.Graph(
                                                id = 'house_map',
                                                #figure = create_map(new_house, house_gj)
                                                )
                                        ]),
                            ]),md=4, className="d-none d-sm-block" #removes map on small devices
                    ),
                dbc.Col(
                 html.Div([
                         dbc.Spinner(color="primary", size='lg',
                             children=[dcc.Graph(
                                             id = 'commdist_map',
                                             #figure = create_map(new_comm_dist, comm_dist_gj)
                                             )
                                     ]),
                         ]),md=4, className="d-none d-sm-block" #removes map on small devices
                 ),
         ],justify="center", id='maps'),

# Data table
        dbc.Row([
            dbc.Col(
                html.Div(
                    dash_table.DataTable(
                                id='the-table',
                                columns=[
                                        {"name": ["", "Id"],
                                        "id": "project_id"},
                                        {"name": ["", "County Region"],
                                        "id": "cook_county_region"},
                                        {"name": ["Districts", "House"],
                                        "id": "house_district"},
                                        {"name": ["Districts", "Senate"],
                                        "id": "senate_district"},
                                        {"name": ["Districts", "Commissioner"],
                                        "id": "commissioner_district"},
                                        {"name": ["", "Project Description"],
                                        "id": "project"},
                                        {"name": ["Project Year Funding", "2021"],
                                        "id": "2021",
                                        'type': 'numeric',
                                        'format': FormatTemplate.money(0)},
                                        {"name": ["Project Year Funding", "2022"],
                                        "id": "2022",
                                        'type': 'numeric',
                                        'format': FormatTemplate.money(0)},
                                        {"name": ["Project Year Funding", "2023"],
                                        "id": "2023",
                                        'type': 'numeric',
                                        'format': FormatTemplate.money(0)},
                                        {"name": ["Project Year Funding", "2024"],
                                        "id": "2024",
                                        'type': 'numeric',
                                        'format': FormatTemplate.money(0)},
                                        {"name": ["", "Total 2021-2024"],
                                        "id": "total_2021_2024",
                                        'type': 'numeric',
                                        'format': FormatTemplate.money(0)},
                                        ],
                                merge_duplicate_headers=True,
                                style_as_list_view=True,
                                data=df.to_dict('records'),
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
                                    'maxWidth': '400px',
                                    'whiteSpace': 'normal',
                                    'color': '#535353'
                                    },
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '17px'
                                    },
                                style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': '#e4e4e7'
                                        }
                                    ],
                                #style_table={'maxHeight': '300px','overflowY': 'scroll'},
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'center'
                                    } for c in ['house_district', 'senate_district', 'commissioner_district']
                                    ],
                                style_header={
                                    'textAlign': 'center',
                                    'fontWeight': 'bold',
                                    'color': 'white',
                                    'backgroundColor': '#A5A5AF'
                                    },
                            ),
                        ), id='div_table',
                    ),
        ],id='row_table'),

# Export button
        dbc.Row([
            dbc.Col(
                html.Div(
                    dbc.Button("Export", color="primary"),
                        ),
                        style={'padding': '5px'},
                        md=4
                    ),
            ]),

        dbc.Row(dbc.Col(html.Div(str(temp_lst)),style={'height': '100px', 'width': 'auto', 'color': 'green'}))

],fluid=True)

layout = html.Div([navbar, body])
