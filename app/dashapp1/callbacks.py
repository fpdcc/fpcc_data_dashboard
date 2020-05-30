import pandas as pd
import psycopg2 as pg
from dash.dependencies import Input
from dash.dependencies import Output
from .layout import * # import stuff from layout.py

def register_callbacks(dashapp):
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
