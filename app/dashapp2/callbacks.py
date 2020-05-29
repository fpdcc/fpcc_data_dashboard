from dash.dependencies import Input
from dash.dependencies import Output
from .layout import *

def register_callbacks(dashapp):
    @dashapp.callback(Output("content", "children"), [Input("tabs", "active_tab")])
    def switch_tab(at):
        if at == "home":
            return "home content"

        elif at == "general":
            return "general content"

        elif at == "details":
            return "details content"
