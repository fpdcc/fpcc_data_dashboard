from datetime import datetime as dt

from dash.dependencies import Input
from dash.dependencies import Output


def register_callbacks(dashapp):
    @dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        return dict({
        "data": [{"type": "bar",
              "x": [1, 2, 3],
              "y": [1, 3, 2]}],
            'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
            })
