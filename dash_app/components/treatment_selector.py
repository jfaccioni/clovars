from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.utils import get_dropdown_index, draw_treatment_curve

if TYPE_CHECKING:
    from dash_app.classes import Curve


class TreatmentSelector(dbc.Container):
    class _IDs:
        name_input = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'name-input',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        frame_input = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'frame-input',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        remove_button = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'remove-treatment-button',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        division_dropdown = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'division-dropdown',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        division_collapse = lambda aio_id, aio_index, curve_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'division-collapse',
            'aio_id': aio_id,
            'aio_index': aio_index,
            'curve_index': curve_index,
        }
        division_inputbox = lambda aio_id, aio_index, curve_index, param_name, param_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'division-inputbox',
            'aio_id': aio_id,
            'aio_index': aio_index,
            'curve_index': curve_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        division_plot = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'division-plot',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        death_dropdown = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'death-dropdown',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        death_collapse = lambda aio_id, aio_index, curve_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'death-collapse',
            'aio_id': aio_id,
            'aio_index': aio_index,
            'curve_index': curve_index,
        }
        death_inputbox = lambda aio_id, aio_index, curve_index, param_name, param_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'death-inputbox',
            'aio_id': aio_id,
            'aio_index': aio_index,
            'curve_index': curve_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        death_plot = lambda aio_id, aio_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'death-plot',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        division_store = lambda aio_id, aio_index : {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'division-store',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }
        death_store = lambda aio_id, aio_index : {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'death-store',
            'aio_id': aio_id,
            'aio_index': aio_index,
        }

    ids = _IDs

    def __init__(
            self,
            curves: list[Curve],
            aio_id: str | dict[str, Any] | None = None,
            aio_index: int | None = None,
    ) -> None:
        """Initializes a TreatmentCurveSelector instance."""
        # AIO vars
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        if aio_index is None:
            aio_index = 0
        id_vars = {'aio_id': aio_id, 'aio_index': aio_index}
        # Other vars
        curve_names = [curve.name for curve in curves]
        # ### DIVISION CURVE COLLAPSABLE PARAMS
        division_collapses = [
            dbc.Collapse(
                id=self.ids.division_collapse(curve_index=curve_index, **id_vars), children=[
                    dbc.InputGroup(
                        class_name='numeric-input-group', children=[
                            dbc.InputGroupText(param.name),
                            dbc.Input(
                                id=self.ids.division_inputbox(
                                    curve_index=curve_index,
                                    param_name=param.name,
                                    param_index=param_index,
                                    **id_vars,
                                    ),
                                type='number',
                                **param.to_dict(),
                            ),
                        ]
                    )
                    for param_index, param in enumerate(curve.params)]
                )
            for curve_index, curve in enumerate(curves)
        ]
        # ### DEATH CURVE COLLAPSABLE PARAMS
        death_collapses = [
            dbc.Collapse(
                id=self.ids.death_collapse(curve_index=curve_index, **id_vars), children=[
                    dbc.InputGroup(
                        class_name='numeric-input-group', children=[
                            dbc.InputGroupText(param.name),
                            dbc.Input(
                                id=self.ids.death_inputbox(
                                    curve_index=curve_index,
                                    param_name=param.name,
                                    param_index=param_index,
                                    **id_vars,
                                ),
                                type='number',
                                **param.to_dict(),
                            ),
                        ]
                    )
                    for param_index, param in enumerate(curve.params)]
            )
            for curve_index, curve in enumerate(curves)
        ]
        # ### GLOBAL
        children = [
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Treatment name"),
                        dbc.Input(id=self.ids.name_input(**id_vars), type='text'),
                    ]),
                ]),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Frame to add"),
                        dbc.Input(id=self.ids.frame_input(**id_vars), type='number')
                    ])
                ]),
                dbc.Col([
                    dbc.Button('Remove this treatment', id=self.ids.remove_button(**id_vars), class_name='btn-primary')
                ])
            ]),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Division Curve'),
                        dcc.Dropdown(id=self.ids.division_dropdown(**id_vars), options=curve_names),
                        *division_collapses,
                        dcc.Graph(id=self.ids.division_plot(**id_vars)),
                    ], align='stretch'),
                    dbc.Col([
                        dbc.Label('Death Curve'),
                        dcc.Dropdown(id=self.ids.death_dropdown(**id_vars), options=curve_names),
                        *death_collapses,
                        dcc.Graph(id=self.ids.death_plot(**id_vars)),
                    ]),
                ]),
            ]),
            dcc.Store(id=self.ids.division_store(**id_vars)),
            dcc.Store(id=self.ids.death_store(**id_vars)),
        ]
        # INIT CALL
        super().__init__(children=children)

    @staticmethod
    @callback(
        Output(ids.division_collapse(MATCH, MATCH, ALL), 'is_open'),
        Input(ids.division_dropdown(MATCH, MATCH), 'value'),
        State(ids.division_dropdown(MATCH, MATCH), 'options'),
    )
    def change_division_curve_params(
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> list[bool]:
        outputs = callback_context.outputs_list
        return change_curve_params(dropdown_value=dropdown_value, dropdown_options=dropdown_options, outputs=outputs)

    @staticmethod
    @callback(
        Output(ids.death_collapse(MATCH, MATCH, ALL), 'is_open'),
        Input(ids.death_dropdown(MATCH, MATCH), 'value'),
        State(ids.death_dropdown(MATCH, MATCH), 'options'),
    )
    def change_death_curve_params(
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> list[bool]:
        outputs = callback_context.outputs_list
        ret = change_curve_params(dropdown_value=dropdown_value, dropdown_options=dropdown_options, outputs=outputs)
        return ret

    @staticmethod
    @callback(
        Output(ids.division_store(MATCH, MATCH), 'data'),
        Input(ids.division_inputbox(MATCH, MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.division_dropdown(MATCH, MATCH), 'value'),
        State(ids.division_dropdown(MATCH, MATCH), 'options'),
        State(ids.division_store(MATCH, MATCH), 'data'),
    )
    def update_division_params(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
            __: dict[str, str | float] | None,  # doesn't really matter since we will overwrite the dictionary
    ) -> dict[str, str | float] | None:
        inputs = callback_context.inputs_list
        return update_params(dropdown_value=dropdown_value, dropdown_options=dropdown_options, inputs=inputs)

    @staticmethod
    @callback(
        Output(ids.death_store(MATCH, MATCH), 'data'),
        Input(ids.death_inputbox(MATCH, MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.death_dropdown(MATCH, MATCH), 'value'),
        State(ids.death_dropdown(MATCH, MATCH), 'options'),
        State(ids.death_store(MATCH, MATCH), 'data'),
    )
    def update_death_params(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
            __: dict[str, str | float] | None,  # doesn't really matter since we will overwrite the dictionary
    ) -> dict[str, str | float] | None:
        inputs = callback_context.inputs_list
        return update_params(dropdown_value=dropdown_value, dropdown_options=dropdown_options, inputs=inputs)

    @staticmethod
    @callback(
        Output(ids.division_plot(MATCH, MATCH), 'figure'),
        Input(ids.division_inputbox(MATCH, MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.division_dropdown(MATCH, MATCH), 'value'),
        State(ids.division_dropdown(MATCH, MATCH), 'options'),
    )
    def draw_division_curve(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> go.Figure:
        inputs = callback_context.inputs_list
        return draw_curve(
            dropdown_value=dropdown_value,
            dropdown_options=dropdown_options,
            inputs=inputs,
            curve_type='division',
        )

    @staticmethod
    @callback(
        Output(ids.death_plot(MATCH, MATCH), 'figure'),
        Input(ids.death_inputbox(MATCH, MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.death_dropdown(MATCH, MATCH), 'value'),
        State(ids.death_dropdown(MATCH, MATCH), 'options'),
    )
    def draw_death_curve(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> go.Figure:
        inputs = callback_context.inputs_list
        return draw_curve(
            dropdown_value=dropdown_value,
            dropdown_options=dropdown_options,
            inputs=inputs,
            curve_type='death',
        )


def change_curve_params(
        dropdown_value: str | None,
        dropdown_options: list[str],
        outputs: list[dict],
) -> list[bool]:
    if not dropdown_value:
        return [False] * len(outputs)
    dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
    return [
        True
        if output['id']['curve_index'] == dropdown_index
        else False
        for output in outputs
    ]


def update_params(
        dropdown_value: str | None,
        dropdown_options: list[str],
        inputs: list[list[dict]],
) -> dict[str, str | float] | None:
    if not dropdown_value:
        return None
    dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
    return get_curve_params(
        params=inputs[0],
        dropdown_value=dropdown_value,
        dropdown_index=dropdown_index,
    )


def draw_curve(
        dropdown_value: str | None,
        dropdown_options: list[str],
        inputs: list[list[dict]],
        curve_type: str,
) -> go.Figure:
    if not dropdown_value:
        fig = go.Figure()
    else:
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        curve_params = get_curve_params(
            params=inputs[0],
            dropdown_value=dropdown_value,
            dropdown_index=dropdown_index,
        )
        fig = draw_treatment_curve(curve_params=curve_params, curve_type=curve_type)
    return fig


def get_curve_params(
        params: list[dict],
        dropdown_value: str,
        dropdown_index: int,
) -> dict[str, str | float]:
    """Returns the parameters of the selected signal."""
    curve_params = {'name': dropdown_value.replace(' ', '').replace('-', '')}
    curve_params.update(
        {
            param['id']['param_name'].lower().replace(' ', '_').replace('-', ''): param['value']
            for param in params
            if param['id']['curve_index'] == dropdown_index
        }
    )
    return curve_params
