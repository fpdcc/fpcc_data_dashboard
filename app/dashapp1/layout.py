# Imports
import sys, os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
import pandas as pd
import pandas.io.sql as psql
from pandas.io.json import json_normalize
import plotly.express as px
import psycopg2 as pg
import numpy as np
import json
import geojson
from pathlib import Path

basedir = Path(os.path.abspath(os.path.dirname(__file__))).parent
datadir = Path(basedir / 'assets')
POSTGRESQL = os.environ.get('POSTGRESQL')
COMMISSIONER_DISTRICT_TABLE = 'public.commdistricts'
SENATE_DISTRICT_TABLE = 'public.il_senate_cb_2017_17_sldu_500k_cc'
HOUSE_DISTRICT_TABLE = 'public.il_house_cb_2017_17_sldl_500k_cc'
DATATABLE = 'public.fpcc_capital_needs_non_mft_21_24'
theme_colors = {
    'header': '#015249',
    'cell_color':'#535353',
    'table_header_color':'#A5A5AF',
    'table_background_color':'#e4e4e7'
    }

def create_map(dataf, geoj):
    """create map with a dataframe and geoJson then update layout"""
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

def gj_query(table, district=None):
    """queries senate, house, or commissioner district tables and returns json to build geojson"""
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        if district is None:
            with connection:
                with cur:
                    # query table for ALL districts
                    query = """SELECT jsonb_build_object('type','FeatureCollection','features', jsonb_agg(feature)) FROM (SELECT jsonb_build_object('type','Feature','id',district,'geometry',ST_AsGeoJSON(st_transform(geom, 4326))::jsonb,'properties',to_jsonb(inputs) - 'geom') AS feature FROM (SELECT id, district, geom FROM {}) inputs) features;""".format(table).replace('\n',' ')

                    cur.execute(query)
                    geoj = cur.fetchall()
                    return geoj
        else:
            with connection:
                with cur:
                    # query table for specific districts
                    query = """SELECT jsonb_build_object('type','FeatureCollection','features', jsonb_agg(feature)) FROM (SELECT jsonb_build_object('type','Feature','id',district,'geometry',ST_AsGeoJSON(st_transform(geom, 4326))::jsonb,'properties',to_jsonb(inputs) - 'geom') AS feature FROM (SELECT id, district, geom FROM {} where district in ('{}')) inputs) features;""".format(table, district).replace('\n',' ')

                    cur.execute(query)
                    geoj = cur.fetchall()
                    return geoj
    finally:
        connection.close()

def output_geojson(jsn):
    """outputs a tuple from sql_query(), to get geojson for map ie. output_geojson()[0], or dict for the maps df ie. output_geojson()[1]."""
    geoj = jsn[0][0]
    geoj2 = json.dumps(geoj)
    geoj3 = geojson.loads(geoj2)
    return (geoj3, geoj)

def table_query():
    """sql query for DataTable"""
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        table_data = pd.read_sql_query('select * from {}'.format(DATATABLE),con=connection)
        return table_data
    finally:
        connection.close()

### create commissioner district geojson ###
comm_dist_gj = output_geojson(gj_query(COMMISSIONER_DISTRICT_TABLE))[0]
# geoj2 = gj[0][0]
# geoj3 = json.dumps(geoj2)
# comm_dist_gj = geojson.loads(geoj3)

### query senate table for geoJson ###
senate_gj = output_geojson(gj_query(SENATE_DISTRICT_TABLE))[0]
# sengeoj2 = sen_query[0][0]
# sengeoj3 = json.dumps(sengeoj2)
# senate_gj = geojson.loads(sengeoj3)

### query house table for geoJson ##
house_gj = output_geojson(gj_query(HOUSE_DISTRICT_TABLE))[0]
# hougeoj2 = house_query[0][0]
# hougeoj3 = json.dumps(hougeoj2)
# house_gj = geojson.loads(hougeoj3)

# df for list of house districts to display on map
house_df = json_normalize(output_geojson(gj_query(HOUSE_DISTRICT_TABLE))[1]['features'])
house_df = pd.DataFrame(house_df.drop(columns=['geometry.coordinates', 'geometry.type', 'id', 'type']))
house_df = house_df.rename(columns={'properties.district': 'district', 'properties.id': 'id'})
hd_list = house_df.astype({'district': 'int32'}).sort_values('district')

# df for list of commissioner districts to display on map
commdist_df = json_normalize(output_geojson(gj_query(COMMISSIONER_DISTRICT_TABLE))[1]['features'])
commdist_df = pd.DataFrame(commdist_df.drop(columns=['geometry.coordinates', 'geometry.type']))
commdist_df = commdist_df.rename(columns={'properties.district': 'district', 'properties.id': 'id'})
cd_list = commdist_df.astype({'district': 'int32'}).sort_values('district')

# df for list of senate districts to display on map
senate_df = json_normalize(output_geojson(gj_query(SENATE_DISTRICT_TABLE))[1]['features'])
senate_df = pd.DataFrame(senate_df.drop(columns=['geometry.coordinates', 'geometry.type', 'id', 'type']))
senate_df = senate_df.rename(columns={'properties.district': 'district', 'properties.id': 'id'})
sd_list = senate_df.astype({'district': 'int32'}).sort_values('district')

##############
# for table
table_df = table_query()
table_df.set_index('id', inplace=True, drop=False)

#map setup

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("CIP", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Data Sets", header=True),
                dbc.DropdownMenuItem("Trails", href="#"),
                dbc.DropdownMenuItem("Parking Lots", href="#"),
                dbc.DropdownMenuItem("Buildings", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="FPCC Data",
    brand_href="#",
    color=theme_colors['header'],
    dark=True,
)

body = dbc.Container(
    children=[

        dbc.Row([
            dbc.Col(
                html.Div("Select a District to filter by.")
            )
        ]),

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
                                                figure = create_map(senate_df, senate_gj)
                                                    )
                                        ]),
                            ]),md=4, className="d-none d-sm-block" #removes map on small devices
                    ),
                dbc.Col(
                    html.Div([
                            dbc.Spinner(color="primary", size="lg",
                                children=[dcc.Graph(
                                                id = 'house_map',
                                                figure = create_map(house_df, house_gj)
                                                )
                                        ]),
                            ]),md=4, className="d-none d-sm-block" #removes map on small devices
                    ),
                dbc.Col(
                     html.Div([
                             dbc.Spinner(color="primary", size='lg',
                                 children=[dcc.Graph(
                                                 id = 'commdist_map',
                                                 figure = create_map(commdist_df, comm_dist_gj)
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
                                export_format='xlsx',
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
                                data=table_df.to_dict('records'),
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
                                    'backgroundColor': theme_colors['table_header_color']
                                    },
                            ),
                        ), id='div_table',
                    ),
            ],id='row_table'),

        dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']}))

],fluid=True)

layout = html.Div([navbar, body])
