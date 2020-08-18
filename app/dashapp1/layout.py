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
from ..assets.dashboard_colors import theme_colors

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
        html.Div([
        dbc.Tabs(
            [
                dbc.Tab(label="CIP Summary", tab_id="summary"),
                dbc.Tab(label="General", tab_id="full_cip")
            ],
            id="tabs",
            active_tab="summary",
            className="nav nav-pills nav-fill mt-3",
            # style={"color": "#00AEF9"}, #inactive tab font color
            # style={"background-color": "#00AEF9"}, #tab background color
        ),
        html.Div(id="content"),
        ]),
        
],fluid=True)

layout = html.Div([navbar, body])
