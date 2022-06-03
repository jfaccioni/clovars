import dash_bootstrap_components as dbc
from dash import Dash, html

from dash_app.run_controls import get_run_controls
from dash_app.colonies_controls import get_colonies_controls

DEBUG = True
THREADED = True

external_stylesheets = [
    # "https://codepen.io/chriddyp/pen/bWLwgP.css",
    dbc.themes.SIMPLEX,
]

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    html.H1("CloVarS App"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(get_run_controls(), label='Globals'),
                dbc.Tab(get_colonies_controls(), label='Colonies'),
                # TODO: add treatment tab
            ]),
        ], md=4),
        dbc.Col(['Hello App'], md=8),
    ], align='center')
] + [html.Br()] * 10, fluid=True)  # TODO: use actual CSS here

if __name__ == '__main__':
    app.run_server(debug=DEBUG, threaded=THREADED)
