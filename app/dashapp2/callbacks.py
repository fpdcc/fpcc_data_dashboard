from dash.dependencies import Input
from dash.dependencies import Output
from .layout import *

def register_callbacks(dashapp):
    @dashapp.callback(Output("content", "children"), [Input("tabs", "active_tab")])
    def switch_tab(at):
        if at == "home":
            card_content = [
                dbc.CardHeader("Card header"),
                dbc.CardBody(
                    [
                        html.H5("Card title", className="card-title"),
                        html.P(
                            "This is some card content that we'll reuse",
                            className="card-text",
                        ),
                    ]
                ),
            ]

            df = pd.DataFrame(
                        {
                    "First Name": ["Arthur", "Ford", "Zaphod", "Trillian"],
                    "Last Name": ["Dent", "Prefect", "Beeblebrox", "Astra"],
                        }
                    )
            home_tab_content = [
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(dbc.Card(card_content, color="primary", inverse=True)),
                            dbc.Col(dbc.Card(card_content, color="secondary", inverse=True)),
                            dbc.Col(dbc.Card(card_content, color="info", inverse=True)),
                        ],
                        className="mb-4 mt-4",
                            ),
                        ),
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                dbc.Table.from_dataframe(
                                    df,
                                    bordered=True,
                                    dark=True,
                                    hover=True,
                                    responsive=True,
                                    striped=True,)
                                ),md=6,
                            ),
                        dbc.Col(
                            html.Div(
                                dbc.Table.from_dataframe(
                                    df,
                                    bordered=True,
                                    dark=True,
                                    hover=True,
                                    responsive=True,
                                    striped=True,)
                                ),md=6,
                            ),
                        ], justify='center'),
                    
                ]
            return home_tab_content

        elif at == "general":
            return "general content"

        elif at == "details":
            return "details content"
