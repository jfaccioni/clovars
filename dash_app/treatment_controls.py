from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import dash
import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc

if TYPE_CHECKING:
    from dash.development.base_component import Component


@dataclass
class Param:
    name: str
    value: float
    min_: float | None = None
    max_: float | None = None
    step_: float | None = None

    def __post_init__(self) -> None:
        if self.min_ is not None and self.value < self.min_:
            raise ValueError(f'Value {self.value} cannot be lower than minimal value ({self.min_})')
        elif self.max_ is not None and self.value > self.max_:
            raise ValueError(f'Value {self.value} cannot be higher than maximal value ({self.max_})')




_PARAMS = [
    _mean := Param('Mean', 0.0, step_=0.05),
    _std := Param('Standard Deviation', 0.05, min_=0.0, step_=0.05),
    _k := Param('K', 1.0, min_=0.0, step_=0.05),
    _a := Param('a', 1.0, min_=0.0, step_=0.05),
    _s := Param('s', 1.0, min_=0.0, step_=0.05),
]

_CURVES = {
    'Gaussian': Curve('Gaussian', params=[_mean, _std]),
    'EM Gaussian': Curve('EM Gaussian', params=[_mean, _std, _k]),
    'Gamma': Curve('Gamma', params=[_mean, _std, _a]),
    'Lognormal': Curve('Lognormal', params=[_mean, _std, _s]),
}


def get_curve_controller() -> html.Div:
    component = html.Div([
        dropdown := dcc.Dropdown([c.type for c in _CURVES.values()]),
        params := dbc.Row([])
    ])

    @dash.callback(
        Output(params, 'children'),
        Input(dropdown, 'value'),
    )
    def select_curve_params(dropdown_value: str | None) -> list[dbc.Col] | None:
        if (signal := _CURVES.get(dropdown_value)) is None:
            return None
        return [
            dbc.Col([
                dbc.Label(p.name),
                dbc.Input(type="number", placeholder='...', value=p.value, min=p.min_, max=p.max_, step=p.step_),
            ])
            for p in _PARAMS
            if p in signal.params
        ]

    return component


def get_treatment_controller() -> html.Div:
    component = html.Div([
        html.Div([
            dbc.Label('Treatment added at frame'),
            dbc.InputGroup([
                frame := dbc.Input(type="number", placeholder='...', value=0, min=0, step=1, max=10_000),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label('Division curve'),
                div_dropdown := dcc.Dropdown([c.type for c in _CURVES.values()]),
                div_params := dbc.Row([]),
            ]),
            dbc.Col([
                dbc.Label('Death curve'),
                dth_dropdown := dcc.Dropdown([c.type for c in _CURVES.values()]),
                dth_params := dbc.Row([]),
                ]),
        ]),
        dbc.Row([
            dbc.Col([
                div_graph := dcc.Graph(),
            ], width=6),
            dbc.Col([
                dth_graph := dcc.Graph(),
            ], width=6),
        ])
    ])

    @dash.callback(
        Output(div_params, 'children'),
        Input(div_dropdown, 'value'),
    )
    def select_division_curve_params(div_dropdown_value) -> list[dbc.Col] | None:
        if (signal := _CURVES.get(div_dropdown_value)) is None:
            return None
        return [
            dbc.Col([
                dbc.Label(p.name),
                dbc.Input(type="number", placeholder='...', value=p.value, min=p.min_, max=p.max_, step=p.step_),
            ], width=6, align='end')
            for p in _PARAMS
            if p in signal.params
        ]

    @dash.callback(
        Output(div_graph, 'figure'),
        Input(div_params, 'children'),
    )
    def update_division_curve_graph(div_curve_params) -> list[dcc.Graph] | None:
        if div_curve_params is None:
            return None
        print(div_curve_params[1].value)

    @dash.callback(
        Output(dth_params, 'children'),
        Input(dth_dropdown, 'value'),
    )
    def select_death_curve_params(death_dropdown_value: str | None) -> list[dbc.Col] | None:
        if (signal := _CURVES.get(death_dropdown_value)) is None:
            return None
        return [
            dbc.Col([
                dbc.Label(p.name),
                dbc.Input(type="number", placeholder='...', value=p.value, min=p.min_, max=p.max_, step=p.step_),
            ], width=6, align='end')
            for p in _PARAMS
            if p in signal.params
        ]

    return component


def get_treatment_regimen_controls() -> dbc.Card:
    treatment_controls = dbc.Card([
        dbc.Label('Treatment Regimen', size='lg'),
        dbc.Row([
            dbc.Col([
                add_treatment_button := dbc.Button('Add treatment'),
            ]),
            dbc.Col([
                remove_treatment_button := dbc.Button('Remove treatment'),
                ]),
        ]),
        html.Br(),  # TODO: replace html.Br with actual CSS and classes for each html element
        treatment_list := html.Div([
            get_treatment_controller(),
        ])
    ], body=True)

    @dash.callback(
        Output(treatment_list, 'children'),
        Input(treatment_list, 'children'),
        Input(add_treatment_button, 'n_clicks'),
        Input(remove_treatment_button, 'n_clicks'),
    )
    def remove_treatment(
            children_list: list[html.Div],
            _: int,
            __: int,
    ) -> list[html.Div]:
        component = get_component_by_id(
            component_id=dash.callback_context.triggered_id,
            components=[add_treatment_button, remove_treatment_button],
        )
        if component is None:  # initial execution - return the input
            return children_list
        elif component == add_treatment_button:
            return children_list + [get_treatment_controller()]
        elif component == remove_treatment_button:
            return children_list[:-1]
        else:
            raise TypeError(f'Got unknown component: {component}')

    return treatment_controls


def get_component_by_id(
    component_id: int,
    components: list[Component],
) -> Component | None:
    """
    Given a list of Components, returns the Component whose ID matches the component_id argument.
    Returns None if no match is found.
    """
    for component in components:
        if component.id == component_id:  # noqa
            return component
    return None
