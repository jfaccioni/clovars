from __future__ import annotations

import pprint

import dash_bootstrap_components as dbc
from dash import Dash, html, Output, State, Input, callback

from dash_app.colonies_tab import get_colonies_tab
from dash_app.globals_tab import get_globals_tab


class Config:
    DEBUG = True
    THREADED = True
    THEME = 'BOOTSTRAP'


def init_app(theme: str) -> Dash:
    """Initializes and returns the Dash app."""
    # INIT APP
    app = Dash(
        __name__,
        external_stylesheets=[getattr(dbc.themes, theme)],
    )
    # LEFT COLUMN
    left_col = dbc.Col(
        md=8,
        children=[
            dbc.Tabs(
                children=[
                    dbc.Tab(get_globals_tab(), label='Globals', className='clovars-tab globals-tab'),
                    dbc.Tab(get_colonies_tab(), label='Colonies', className='clovars-tab colonies-tab'),
                    # dbc.Tab(get_treatment_regimen_controls(), label='Treatment Regimen'),
                ],
            ),
        ],
    )
    # RIGHT_COLUMN
    right_col = dbc.Col(
        md=4,
        align='start',
        children=[
            dbc.Button('Run CloVarS!', id='run-clovars-button', size='lg'),
        ],
    )
    # MAIN APP LAYOUT
    app.layout = dbc.Container(
        fluid=True,
        children=[
            html.H1("CloVarS App", className='text-dark'),
            html.Hr(),
            dbc.Row(
                align='center',
                children=[
                    left_col,
                    right_col,
                ],
            ),
            html.Div(id='dummy-div-main', className='dummy-div'),
        ],
    )
    padding = [html.Br()] * 10
    app.layout.children += padding  # TODO: use actual CSS here
    return app


# ### GLOBAL APP CALLBACKS

@callback(
    Output('dummy-div-main', 'children'),
    State('globals-store', 'data'),
    State('colonies-store', 'data'),
    State({'component': 'SignalSelector', 'subcomponent': 'store', 'aio_id': 'colonies-signal-selector'}, 'data'),
    Input('run-clovars-button', 'n_clicks'),
)
def display_parameters(
        global_data: dict,
        colonies_data: dict,
        cell_signal_data: dict,
        n_clicks: int,
) -> None:
    """Displays the current parameters on the console."""
    if n_clicks is not None:
        data = {
            'global': global_data,
            'colonies': colonies_data,
            'cell_signal': cell_signal_data,
        }
        print("Total data:\n")
        pprint.pprint(data, sort_dicts=False)
    return None


if __name__ == '__main__':
    dash_app = init_app(theme=Config.THEME)
    dash_app.run_server(debug=Config.DEBUG, threaded=Config.THREADED)
