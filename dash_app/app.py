from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash, html, Output, State, Input, callback

from dash_app.tabs import get_clovars_tabs


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
    left_col = dbc.Col(get_clovars_tabs(), md=8)
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
    State('treatment-regimen-store', 'data'),
    Input('run-clovars-button', 'n_clicks'),
)
def display_parameters(
        global_data: dict,
        colonies_data: dict,
        signal_data: dict,
        treatment_regimen_data: dict,
        n_clicks: int,
) -> None:
    """Displays the current parameters on the console."""
    if n_clicks is not None:
        data = {
            'global': global_data,
            'colonies': colonies_data,
            'cell_signal': signal_data,
            'treatment_regimen_data': treatment_regimen_data,
        }
        print("Total data:\n")
        import pprint
        pprint.pprint(data, sort_dicts=False)
    return None


if __name__ == '__main__':
    dash_app = init_app(theme=Config.THEME)
    dash_app.run_server(debug=Config.DEBUG, threaded=Config.THREADED)
