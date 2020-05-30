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
import plotly.express as px
import psycopg2 as pg
import numpy as np
import json
import geojson
from pathlib import Path

basedir = Path(os.path.abspath(os.path.dirname(__file__))).parent
datadir = Path(basedir / 'assets')
POSTGRESQL = os.environ.get('POSTGRESQL')

#project data
conn_string=POSTGRESQL
connection=pg.connect(conn_string)
cur = connection.cursor()

theme_colors = {
    'header': '#015249',
    'cell_color':'#535353',
    'table_header_color':'#A5A5AF',
    'table_background_color':'#e4e4e7'
    }

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Buildings", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Data Sets", header=True),
                dbc.DropdownMenuItem("Trails", href="#"),
                dbc.DropdownMenuItem("Parking Lots", href="#"),
                dbc.DropdownMenuItem("Picnic Groves", href="#"),
                dbc.DropdownMenuItem("CIP", href="#"),
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
        html.Div([
        dbc.Tabs(
            [
                dbc.Tab(label="Home", tab_id="home"),
                dbc.Tab(label="General", tab_id="general"),
                dbc.Tab(label="Details", tab_id="details"),
            ],
            id="tabs",
            active_tab="home",
            className="nav nav-pills nav-fill mt-3",
            # style={"color": "#00AEF9"}, inactive tabe font color
            # style={"background-color": "#00AEF9"}, tab background color
        ),
        html.Div(id="content"),
        ]),



    ],fluid=True)

layout = html.Div([navbar, body])
