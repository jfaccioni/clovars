from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.utils import get_dropdown_index, draw_treatment_curve, get_treatment_curves

if TYPE_CHECKING:
    from dash_app.classes import Curve


class TreatmentSelector(dbc.Container):
    class _IDs:
        name_input = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'name-input',
            'aio_id': aio_id,
        }
        frame_input = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'frame-input',
            'aio_id': aio_id,
        }
        remove_button = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'remove-treatment-button',
            'aio_id': aio_id,
        }
        division_dropdown = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'division-dropdown',
            'aio_id': aio_id,
        }
        division_collapse = lambda aio_id, curve_index: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'division-collapse',
            'aio_id': aio_id,
            'curve_index': curve_index,
        }
        division_inputbox = lambda aio_id, curve_index, param_name, param_index: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'division-inputbox',
            'aio_id': aio_id,
            'curve_index': curve_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        division_plot = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'division-plot',
            'aio_id': aio_id,
        }
        death_dropdown = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'death-dropdown',
            'aio_id': aio_id,
        }
        death_collapse = lambda aio_id, curve_index: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'death-collapse',
            'aio_id': aio_id,
            'curve_index': curve_index,
        }
        death_inputbox = lambda aio_id, curve_index, param_name, param_index: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'death-inputbox',
            'aio_id': aio_id,
            'curve_index': curve_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        death_plot = lambda aio_id: {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'death-plot',
            'aio_id': aio_id,
        }
        store = lambda aio_id : {  # noqa
            'component': 'TreatmentSelector',
            'subcomponent': 'store',
            'aio_id': aio_id,
        }

    ids = _IDs

    def __init__(
            self,
            aio_id: str | dict[str, Any] | None = None,
            curves: list[Curve] = None,
    ) -> None:
        """Initializes a TreatmentCurveSelector instance."""
        # AIO vars
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        # Other vars
        if curves is None:
            curves = get_treatment_curves()
        curve_names = [curve.name for curve in curves]
        # ### DIVISION CURVE COLLAPSABLE PARAMS
        division_collapses = [
            dbc.Collapse(
                id=self.ids.division_collapse(aio_id=aio_id, curve_index=curve_index), children=[
                    dbc.InputGroup(
                        class_name='numeric-input-group', children=[
                            dbc.InputGroupText(param.name),
                            dbc.Input(
                                id=self.ids.division_inputbox(
                                    aio_id=aio_id,
                                    curve_index=curve_index,
                                    param_name=param.name,
                                    param_index=param_index,
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
                id=self.ids.death_collapse(aio_id=aio_id, curve_index=curve_index), children=[
                    dbc.InputGroup(
                        class_name='numeric-input-group', children=[
                            dbc.InputGroupText(param.name),
                            dbc.Input(
                                id=self.ids.death_inputbox(
                                    aio_id=aio_id,
                                    curve_index=curve_index,
                                    param_name=param.name,
                                    param_index=param_index,
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
        initial_data = {
            'division_curve': {
                'name': 'Gaussian',
                'params': {param.name: param.value for param in curves[0].params},
            },
            'death_curve': {
                'name': 'EM Gaussian',
                'params': {param.name: param.value for param in curves[1].params},
            },
            'added_on_frame': 0,
        }
        # ### GLOBAL
        children = [
            dbc.Row([
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Treatment name"),
                        dbc.Input(id=self.ids.name_input(aio_id=aio_id), type='text', value='Control'),
                    ]),
                ]),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.InputGroupText("Frame to add"),
                        dbc.Input(id=self.ids.frame_input(aio_id=aio_id), type='number', value=0)
                    ])
                ]),
                dbc.Col([
                    dbc.Button(
                        'Remove this treatment',
                        id=self.ids.remove_button(aio_id=aio_id),
                        class_name='btn-primary',
                    )
                ])
            ]),
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        dbc.Label('Division Curve'),
                        dcc.Dropdown(
                            id=self.ids.division_dropdown(aio_id=aio_id),
                            options=curve_names,
                            value='Gaussian',
                        ),
                        *division_collapses,
                        dcc.Graph(id=self.ids.division_plot(aio_id=aio_id)),
                    ], align='stretch'),
                    dbc.Col([
                        dbc.Label('Death Curve'),
                        dcc.Dropdown(
                            id=self.ids.death_dropdown(aio_id=aio_id),
                            options=curve_names,
                            value='EM Gaussian',
                        ),
                        *death_collapses,
                        dcc.Graph(id=self.ids.death_plot(aio_id=aio_id)),
                    ]),
                ]),
            ]),
            dcc.Store(id=self.ids.store(aio_id=aio_id), data=initial_data),
        ]
        # INIT CALL
        super().__init__(id=aio_id, children=children, class_name='border border-primary border-round')

    @staticmethod
    @callback(
        Output(ids.division_collapse(MATCH, ALL), 'is_open'),
        Input(ids.division_dropdown(MATCH), 'value'),
        State(ids.division_dropdown(MATCH), 'options'),
    )
    def change_division_curve_params(
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> list[bool]:
        outputs = callback_context.outputs_list
        return change_curve_params(dropdown_value=dropdown_value, dropdown_options=dropdown_options, outputs=outputs)

    @staticmethod
    @callback(
        Output(ids.death_collapse(MATCH, ALL), 'is_open'),
        Input(ids.death_dropdown(MATCH), 'value'),
        State(ids.death_dropdown(MATCH), 'options'),
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
        Output(ids.store(MATCH), 'data'),
        Input(ids.division_inputbox(MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.death_inputbox(MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.division_dropdown(MATCH), 'value'),
        Input(ids.death_dropdown(MATCH), 'value'),
        Input(ids.frame_input(MATCH), 'value'),
        State(ids.division_dropdown(MATCH), 'options'),
        State(ids.death_dropdown(MATCH), 'options'),
        State(ids.store(MATCH), 'data'),
    )
    def update_params_store(
            _: list[float | None],  # we want the division inputs to trigger the callback, but the values don't matter
            __: list[float | None],  # we want the death inputs to trigger the callback, but the values don't matter
            division_dropdown_value: str | None,
            death_dropdown_value: str | None,
            frame_number: int | None,
            division_dropdown_options: list[str],
            death_dropdown_options: list[str],
            treatment_data: dict[str, int | dict[str, str | float]] | None,
    ) -> dict[str, str | float] | None:
        if not (triggered_id := callback_context.triggered_id):
            return treatment_data
        if triggered_id['subcomponent'].startswith('frame'):  # triggered by a change in the frame number
            treatment_data['added_on_frame'] = frame_number
            return treatment_data
        if triggered_id['subcomponent'].startswith('division'):  # triggered by a change in a division parameter
            dropdown_value = division_dropdown_value
            dropdown_options = division_dropdown_options
            param_list = callback_context.inputs_list[0]
            curve_name = 'division_curve'
        elif triggered_id['subcomponent'].startswith('death'):  # triggered by a change in a division parameter
            dropdown_value = death_dropdown_value
            dropdown_options = death_dropdown_options
            param_list = callback_context.inputs_list[1]
            curve_name = 'death_curve'
        else:
            raise ValueError(f"Got unknown ID: {triggered_id}.")
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        params = get_curve_params(param_list=param_list, dropdown_value=dropdown_value, dropdown_index=dropdown_index)
        treatment_data[curve_name] = params
        return treatment_data

    @staticmethod
    @callback(
        Output(ids.division_plot(MATCH), 'figure'),
        Input(ids.division_inputbox(MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.division_dropdown(MATCH), 'value'),
        State(ids.division_dropdown(MATCH), 'options'),
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
        Output(ids.death_plot(MATCH), 'figure'),
        Input(ids.death_inputbox(MATCH, ALL, ALL, ALL), 'value'),
        Input(ids.death_dropdown(MATCH), 'value'),
        State(ids.death_dropdown(MATCH), 'options'),
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
            param_list=inputs[0],
            dropdown_value=dropdown_value,
            dropdown_index=dropdown_index,
        )
        fig = draw_treatment_curve(curve_params=curve_params, curve_type=curve_type)
    return fig


def get_curve_params(
        param_list: list[dict],
        dropdown_value: str,
        dropdown_index: int,
) -> dict[str, str | float]:
    """Returns the parameters of the selected signal."""
    curve_params = {'name': dropdown_value.replace(' ', '').replace('-', '')}
    curve_params.update(
        {
            param['id']['param_name'].lower().replace(' ', '_').replace('-', ''): param['value']
            for param in param_list
            if param['id']['curve_index'] == dropdown_index
        }
    )
    return curve_params
