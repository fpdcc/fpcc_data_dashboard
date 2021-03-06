import dash
import dash_bootstrap_components as dbc
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required

from config import BaseConfig


def create_app():
    server = Flask(__name__)
    server.config.from_object(BaseConfig)

    from app.dashapp1.layout import layout as layout1 # CIP
    from app.dashapp1.callbacks import register_callbacks as register_callbacks1
    register_dashapp(server, 'Dashapp 1', 'dashapp1', layout1, register_callbacks1)

    from app.dashapp2.layout import layout as layout2 # Building
    from app.dashapp2.callbacks import register_callbacks as register_callbacks2
    register_dashapp(server, 'Dashapp 2', 'dashapp2', layout2, register_callbacks2)

    from app.dashapp3.layout import layout as layout3 # trails
    from app.dashapp3.callbacks import register_callbacks as register_callbacks3
    register_dashapp(server, 'Dashapp 3', 'dashapp3', layout3, register_callbacks3)

    from app.dashapp4.layout import layout as layout4 # parking lots
    from app.dashapp4.callbacks import register_callbacks as register_callbacks4
    register_dashapp(server, 'Dashapp 4', 'dashapp4', layout4, register_callbacks4)

    from app.dashapp5.layout import layout as layout5 # parcels licenses
    from app.dashapp5.callbacks import register_callbacks as register_callbacks5
    register_dashapp(server, 'Dashapp 5', 'dashapp5', layout5, register_callbacks5)

    register_extensions(server)
    register_blueprints(server)

    return server


def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    my_dashapp = dash.Dash(__name__,
                           server=app,
                           url_base_pathname=f'/{base_pathname}/',
                           assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
                           meta_tags=[meta_viewport],
                           external_stylesheets=[dbc.themes.FLATLY])

    my_dashapp.scripts.config.serve_locally = False

    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    _protect_dashviews(my_dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_extensions(server):
    from app.extensions import db
    from app.extensions import login
    from app.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
