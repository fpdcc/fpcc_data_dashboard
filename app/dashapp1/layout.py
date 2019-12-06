import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H1('Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Sam', 'value': 'COKE'},
            {'label': 'Phil', 'value': 'TSLA'},
            {'label': 'Tom', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})
