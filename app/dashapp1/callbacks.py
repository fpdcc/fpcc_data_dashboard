import pandas as pd
import psycopg2 as pg
from dash.dependencies import Input
from dash.dependencies import Output
from .layout import *

def sql_query(table, district):
    try:
        conn_string=POSTGRESQL
        connection=pg.connect(conn_string)
        cur = connection.cursor()
    except Exception as e :
        print("[!] ",e)
    else:
        with connection:
            with cur:
                # query table for geoJson
                query = """SELECT jsonb_build_object(
                'type','FeatureCollection',
                'features', jsonb_agg(feature)
                )
                FROM (
                SELECT jsonb_build_object(
                'type','Feature',
                'id', name,
                'geometry', ST_AsGeoJSON(st_transform(geom, 4326))::jsonb,
                'properties', to_jsonb(inputs) - 'geom'
                ) AS feature
                FROM (
                SELECT * FROM public.{} where name in ('{}')) inputs) features;""".format(table, district).replace('\n',' ')

                cur.execute(query)
                geoj = cur.fetchall()
                geoj2 = geoj[0][0]
                geoj3 = json.dumps(geoj2)
                # new geojson
                newgeoj = geojson.loads(geoj3)

                return newgeoj
    finally:
        connection.close()

def register_callbacks(dashapp):
    # update commissioner district map with dropdpwn
    @dashapp.callback(
        Output('commdist_map', 'figure'),
        [Input('commdist_dropdown', 'value')])
    def update_commdist_map(commdist_dropdown):
        if commdist_dropdown not in [ns for ns in cd_list['district']]:
            return create_map(commdist_df, comm_dist_gj)
        elif commdist_dropdown in [ns for ns in cd_list['district']]:
            # return create_map()
            selected_commdist_gj = sql_query('commdistricts', commdist_dropdown)
            selected_commdist_df = commdist_df.loc[commdist_df['district'].isin(str(commdist_dropdown))]
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
