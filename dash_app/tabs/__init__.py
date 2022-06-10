from __future__ import annotations

import dash_bootstrap_components as dbc

from dash_app.tabs.colonies_tab import get_colonies_tab
from dash_app.tabs.globals_tab import get_globals_tab


def get_clovars_tabs() -> dbc.Tabs:
    """Returns the tabs used by CloVarS."""
    return dbc.Tabs([
        dbc.Tab(get_globals_tab(), label='Globals', className='clovars-tab globals-tab'),
        dbc.Tab(get_colonies_tab(), label='Colonies', className='clovars-tab colonies-tab'),
        # dbc.Tab(get_treatment_regimen_controls(), label='Treatment Regimen'),
    ])
