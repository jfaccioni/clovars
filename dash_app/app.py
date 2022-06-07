from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash, html, Output, State, Input, callback

from dash_app.globals_tab import get_globals_tab
from dash_app.colonies_tab import get_colonies_tab


class Config:
    DEBUG = True
    THREADED = True
    THEME = 'SIMPLEX'


def init_app(theme: str) -> Dash:
    """Initializes and returns the Dash app."""
    app = Dash(
        __name__,
        external_stylesheets=[getattr(dbc.themes, theme)],
    )
    app.layout = dbc.Container([
        html.H1("CloVarS App"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(get_globals_tab(), label='Globals'),
                    dbc.Tab(get_colonies_tab(), label='Colonies'),
                    # dbc.Tab(get_treatment_regimen_controls(), label='Treatment Regimen'),
                    ]),
            ], md=4),
            dbc.Col([
                dbc.Button('Run CloVarS!', id='run-clovars-button', size='lg'),
            ], md=8),
        ], align='center'),
        html.Div(id='dummy-div-main', style={'display': 'none'}),
    ], fluid=True)
    padding = [html.Br()] * 10
    app.layout.children += padding  # TODO: use actual CSS here
    return app


# ### CALLBACKS

@callback(
    Output('dummy-div-main', 'children'),
    State('globals-store', 'data'),
    State('colonies-store', 'data'),
    Input('run-clovars-button', 'n_clicks'),
)
def display_parameters(
        global_data: dict,
        colonies_data: dict,
        _: int,  # n_clicks
) -> None:
    """Displays the current parameters on the console."""
    data = global_data.copy()
    data.update(colonies_data)
    print("Total data:\n", data)
    return None


if __name__ == '__main__':
    app = init_app(theme=Config.THEME)
    app.run_server(debug=Config.DEBUG, threaded=Config.THREADED)
