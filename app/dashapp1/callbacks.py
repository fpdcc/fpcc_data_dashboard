import pandas as pd
import psycopg2 as pg
from dash.dependencies import Input
from dash.dependencies import Output
from .layout import * # import stuff from layout.py

POSTGRESQL = os.environ.get('POSTGRESQL')
COMMISSIONER_DISTRICT_TABLE = 'public.commdistricts'
SENATE_DISTRICT_TABLE = 'public.il_senate_cb_2017_17_sldu_500k_cc'
HOUSE_DISTRICT_TABLE = 'public.il_house_cb_2017_17_sldl_500k_cc'
DATATABLE = 'public.cip2020_final1_7_2020'

def create_map(dataf, geoj):
    """create map with a dataframe and geoJson then update layout"""
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
        conn_string = POSTGRESQL
        connection = pg.connect(conn_string)
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
    """outputs a tuple from gj_query().
    To get geojson for map use output_geojson()[0],
    To get dict for the map df use output_geojson()[1]."""
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

def summary_tables(df_table):
    """ return a category title and summary table for each category found in the CIP table."""
    table_cats = []
    df_table_catvals = df_table.category.unique()
    for t in df_table_catvals:
        table_cat = df_table[df_table.category == t]
        table_cat = pd.pivot_table(table_cat, index=['subcategory'], aggfunc=np.sum, margins=True, margins_name="total")
        table_cat = table_cat.reset_index()
        table_cats.append((t,table_cat))
        
    sum_layout = []
    for t in table_cats:
        c,l = t 
        table_id = "table" + c
        tbl = dash_table.DataTable(
                id=table_id,
                data=l.to_dict('records'),
                columns=[{"name": i, "id": i} for i in l.columns],
                # columns=[
                #         {"name": ["", "Project Category"],
                #         "id": "subcategory"},
                #         {"name": ["2020 Funds", "Existing C&D Funds"],
                #         "id": "rollover_cd",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["2020 Funds", "2019 Bond Funds"],
                #         "id": "bond",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["2020 Funds", "Grants & Fees"],
                #         "id": "grant_funds", 
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["2020 Funds", "2020 New C&D Funds"],
                #         "id": "new_cd_funds_2020",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["2020 Funds", "Total 2020 Funds"],
                #         "id": "all_2020_total",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["Project Year Funding", "Unfunded 2021-2024"],
                #         "id": "21_24_total",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         {"name": ["Project Year Funding", "Total Est. Project Cost 2020-2024"],
                #         "id": "est_proj_cost_20_24",
                #         'type': 'numeric',
                #         'format': FormatTemplate.money(0)},
                #         ],
                merge_duplicate_headers=True,
                style_as_list_view=False,
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'height': 'auto',
                    'minWidth': '35px',
                    'maxWidth': '50px',
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
                        },
                        {
                            'if': {
                                'filter_query': '{subcategory} = "total"'
                                },
                            'backgroundColor': '#0074D9',
                            'color': 'white'
                        },
                    ],
                style_header={
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'color': 'white',
                    'backgroundColor': theme_colors['table_header_color']
                    },
                )
        ctg = html.Div(html.H3(c.title()))
        sum_layout.append(ctg)
        sum_layout.append(html.Div(tbl))
    return sum_layout

###################
# Create GeoJsons #
###################

### create commissioner district geojson ###
comm_dist_gj = output_geojson(gj_query(COMMISSIONER_DISTRICT_TABLE))[0]

### query senate table for geoJson ###
senate_gj = output_geojson(gj_query(SENATE_DISTRICT_TABLE))[0]

### query house table for geoJson ###
house_gj = output_geojson(gj_query(HOUSE_DISTRICT_TABLE))[0]


#######################
# DFs for map display #
#######################

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

# df for list of house districts to display on map
house_df = json_normalize(output_geojson(gj_query(HOUSE_DISTRICT_TABLE))[1]['features'])
house_df = pd.DataFrame(house_df.drop(columns=['geometry.coordinates', 'geometry.type', 'id', 'type']))
house_df = house_df.rename(columns={'properties.district': 'district', 'properties.id': 'id'})
hd_list = house_df.astype({'district': 'int32'}).sort_values('district')

#############
# CIP table #
#############
table_df = table_query()
table_df.set_index('cip_id', inplace=True, drop=False)

######################
# CIP Summary tables #
######################

### Capital Spending by Funding Source ###

# get table without new amenities
table1 = table_df[table_df["new_amenity"].isnull()]

# group table by category and subcategory
table1_group = table1.groupby(['category', 'subcategory']).sum()

# total all unfunded years 2021 - 2024 put in new col
table1_group['21_24_total'] = table1_group[['yr2021', 'yr2022', 'yr2023', 'yr2024']].sum(axis=1)

# total current year funds put in new col
table1_group['all_2020_total'] = table1_group[['rollover_cd', 'bond', 'grant_funds', 'new_cd_funds_2020']].sum(axis=1)

# total project costs across all years put in new col
table1_group['est_proj_cost_20_24'] = table1_group[['21_24_total', 'all_2020_total']].sum(axis=1)

# reset index
table1_group_reset = table1_group.reset_index()

# drop cols that are no longer needed
table1_group_reset = table1_group_reset.drop(columns=['cip_id', 'yr2021', 'yr2022', 'yr2023', 'yr2024', 'total_2020', 'total_2021_2024'])

### Projected Annaul Need table ###



def register_callbacks(dashapp):
    @dashapp.callback(Output("content", "children"), [Input("tabs", "active_tab")])
    def switch_tab(at):
        if at == "summary":

            summary_cip_tab = [
                
                # capital funding by source table
                html.Div([
                    html.H1("Capital Funding by Source"),
                    html.Div(summary_tables(table1_group_reset)),
                ]),

                # annual need
                html.Div([
                    html.H1("Projected Annual Need"),
                    html.Div(summary_tables(table1_group_reset)),
                ]),
                
                 # footer
                dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']}))        

            ]
            return summary_cip_tab

        elif at == "full_cip":
            full_cip_tab_content = [
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
                                                        #figure = create_map(senate_df, senate_gj)
                                                            )
                                                ]),
                                    ]),md=4, className="d-none d-sm-block" #removes map on small devices
                            ),
                        dbc.Col(
                            html.Div([
                                    dbc.Spinner(color="primary", size="lg",
                                        children=[dcc.Graph(
                                                        id = 'house_map',
                                                        #figure = create_map(house_df, house_gj)
                                                        )
                                                ]),
                                    ]),md=4, className="d-none d-sm-block" #removes map on small devices
                            ),
                        dbc.Col(
                            html.Div([
                                    dbc.Spinner(color="primary", size='lg',
                                        children=[dcc.Graph(
                                                        id = 'commdist_map',
                                                        # figure = create_map(commdist_df, comm_dist_gj)
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
                                                "id": "cip_id"},
                                                {"name": ["", "Category"],
                                                "id": "category"},
                                                {"name": ["", "Sub-Category"],
                                                "id": "subcategory"},
                                                {"name": ["", "FPCC Zone"],
                                                "id": "zone"},
                                                {"name": ["", "Project Description"],
                                                "id": "project_description"},
                                                {"name": ["", "Other"],
                                                "id": "other"},
                                                {"name": ["", "Funded"],
                                                "id": "funded"},
                                                {"name": ["", "Priority"],
                                                "id": "priority"},
                                                {"name": ["", "New Amenity"],
                                                "id": "new_amenity"},
                                                {"name": ["2020 Funds", "Rollover CD"],
                                                "id": "rollover_cd",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["2020 Funds", "Bond"],
                                                "id": "bond",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["2020 Funds", "Grant"],
                                                "id": "grant_funds", 
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["2020 Funds", "2020 New CD Funds"],
                                                "id": "new_cd_funds_2020",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["2020 Funds", "Total 2020 Funds"],
                                                "id": "total_2020",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["Project Year Funding", "2021"],
                                                "id": "yr2021",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["Project Year Funding", "2022"],
                                                "id": "yr2022",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["Project Year Funding", "2023"],
                                                "id": "yr2023",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["Project Year Funding", "2024"],
                                                "id": "yr2024",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                {"name": ["Project Year Funding", "Total 2021-2024"],
                                                "id": "total_2021_2024",
                                                'type': 'numeric',
                                                'format': FormatTemplate.money(0)},
                                                ],
                                        merge_duplicate_headers=True,
                                        style_as_list_view=False,
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
                                ), id='div_table',
                            ),
                    ],id='row_table'),

                # footer
                dbc.Row(dbc.Col(html.Div(),style={'height': '100px', 'width': 'auto', 'background-color': theme_colors['header']}))                
            ]
            return full_cip_tab_content
    
    # update commissioner district map with dropdown
    @dashapp.callback(
        Output('commdist_map', 'figure'),
        [Input('commdist_dropdown', 'value')])
    def update_commdist_map(commdist_dropdown):
        # if commdist_dropdown not in [ns for ns in cd_list['district']]:
        if commdist_dropdown == 0:
            return create_map(commdist_df, comm_dist_gj)
        else:
            selected_commdist_gj = output_geojson(gj_query(COMMISSIONER_DISTRICT_TABLE, commdist_dropdown))[0]
            selected_commdist_df = commdist_df.loc[commdist_df['district'].isin([str(commdist_dropdown)])]
            return create_map(selected_commdist_df, selected_commdist_gj)

    # update senate district map with drop down
    @dashapp.callback(
        Output('senate_map', 'figure'),
        [Input('senate_dropdown', 'value')])
    def update_senate_map(senate_dropdown):
        if senate_dropdown == 0:
            return create_map(senate_df, senate_gj)
        elif senate_dropdown in [ns for ns in sd_list['district']]:
            selected_senate_gj = sql_query('il_senate_cb_2017_17_sldu_500k_cc', senate_dropdown)
            selected_senate_df = senate_df.loc[senate_df['district'].isin(senate_dropdown)]
            return create_map(selected_senate_df, selected_senate_gj)

    # update house district map with drop down
    @dashapp.callback(
        Output('house_map', 'figure'),
        [Input('house_dropdown', 'value')])
    def update_house_map(house_dropdown):
        if house_dropdown == 0:
            return create_map(house_df, house_gj)
        else:
            selected_house_gj = sql_query('il_house_cb_2017_17_sldl_500k_cc', house_dropdown)
            selected_house_df = house_df.loc[house_df['district'].isin(house_dropdown)]
            return create_map(selected_house_df, selected_house_gj)