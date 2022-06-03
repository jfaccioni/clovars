from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output


def get_switch_and_value_box(
        switch_enabled: bool = False,
        switch_label: str = "",
        input_placeholder: str = "",
        value: int | None = None,
        _min: int | None = None,
        _max: int | None = None,
        step: int | None = None,
        end_label: str = "",
) -> dbc.InputGroup:
    component = dbc.InputGroup([
        dbc.InputGroupText(
            switch := dbc.Checkbox(value=switch_enabled, label=switch_label)
        ),
        number_input := dbc.Input(
            type="number",
            placeholder=input_placeholder,
            value=value if switch_enabled is True else None,
            min=_min,
            max=_max,
            step=step,
        ),
        dbc.InputGroupText(end_label) if end_label else None,
    ])

    @dash.callback(
        Output(number_input, 'disabled'),
        Input(switch, 'value'),
    )
    def set_input_active(switch_is_active: bool) -> bool:
        return not switch_is_active

    @dash.callback(
        Output(number_input, 'value'),
        Input(switch, 'value'),
    )
    def set_input_value(switch_is_active: bool) -> int | None:
        return value if switch_is_active is True else None

    return component


def get_run_controls() -> dbc.Card:
    run_controls = dbc.Card([
        dbc.Label('Simulation Parameters', size='lg'),
        html.Br(),
        html.Div([
            dbc.Label('Delta between frames'),
            dbc.InputGroup([
                delta := dbc.Input(type="number", placeholder='...', value=3600, min=0, step=100, ),
                dbc.InputGroupText('seconds')
            ]),
        ]),
        html.Br(),
        html.Div([
            dbc.Label('Stop Conditions'),
            stop_at_frame := get_switch_and_value_box(
                switch_enabled=True,
                switch_label='Stop after iterating for',
                input_placeholder='...',
                value=144,
                end_label='frames'
            ),
            html.Br(),
            get_switch_and_value_box(
                switch_label='Stop when a colony reaches',
                input_placeholder='...',
                value=100,
                end_label='cells'
            ),
            html.Br(),
            get_switch_and_value_box(
                switch_label='Stop when all colonies reach',
                input_placeholder='...',
                value=50,
                end_label='cells'
            ),
        ]),
        html.Br(),
        html.Div([
            time_label := dbc.Label(),
        ]),
    ], body=True)

    @dash.callback(
        Output(time_label, 'children'),
        Input(delta, 'value'),
        Input(stop_at_frame.children[1], 'value'),
    )
    def set_total_runtime(
            delta: int,
            n_frames: int | None,
    ) -> str:
        if n_frames is None:
            return ""
        total_seconds = (delta * n_frames)
        total_hours = total_seconds / (60 * 60)
        total_days = total_hours / 24
        return f"Simulation will run for {round(total_hours, 3)} hours ({round(total_days, 3)} days)"

    return run_controls
