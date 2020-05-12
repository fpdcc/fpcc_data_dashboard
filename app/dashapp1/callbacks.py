import pandas as pd
import geopandas as gpd
from dash.dependencies import Input
from dash.dependencies import Output
from .layout import *


def register_callbacks(dashapp):
    # update commissioner district map with dropdpwn
    @dashapp.callback(
        Output('commdist_map', 'figure'),
        [Input('commdist_dropdown', 'value')])
    def update_commdist_map(commdist_dropdown):
        if commdist_dropdown not in [ns for ns in cd_list['district']]:
            return create_map(new_comm_dist, comm_dist_gj)
        else:
            # return create_map()
            selected_commdist_gj = comm_dist_gj.loc[comm_dist_gj['district'].isin([str(commdist_dropdown)])]
            selected_commdist_df = new_comm_dist.loc[new_comm_dist['district'].isin(str(commdist_dropdown))]
            # selected_commdist_gj = comm_dist_gj.loc[comm_dist_gj['district'] == str(comm_dist_dropdown)]
            # selected_commdist_df = new_comm_dist.loc[new_comm_dist['district'] == str(comm_dist_dropdown)]
            return create_map(selected_commdist_df, selected_commdist_gj)

    # update senate district map with drop down
    @dashapp.callback(
        Output('senate_map', 'figure'),
        [Input('senate_dropdown', 'value')])
    def update_senate_map(senate_dropdown):
        if senate_dropdown == 0:
            return create_map(new_senate, senate_gj)
        else:
            selected_senate_gj = senate_gj.loc[senate_gj['district'].isin(senate_dropdown)]
            selected_senate_df = new_senate.loc[new_senate['district'].isin(senate_dropdown)]
            return create_map(selected_senate_df, selected_senate_gj)

    # update house district map with drop down
    @dashapp.callback(
        Output('house_map', 'figure'),
        [Input('house_dropdown', 'value')])
    def update_house_map(house_dropdown):
        if house_dropdown == 0:
            return create_map(new_house, house_gj)
        else:
            selected_house_gj = house_gj.loc[house_gj['district'].isin(house_dropdown)]
            selected_house_df = new_house_dist.loc[new_comm_dist['district'].isin(house_dropdown)]
            return create_map(selected_house_df, selected_house_gj)
