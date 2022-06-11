from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.utils import get_dropdown_index, draw_treatment_curve

if TYPE_CHECKING:
    from dash_app.classes import Curve


class TreatmentCurveSelector(dbc.Container):
    class _IDs:
        dropdown = lambda aio_id, treatment_index, curve_type: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'dropdown',
            'aio_id': aio_id,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
        }
        collapse = lambda aio_id, treatment_index, curve_type, curve_name, curve_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'inputgroup',
            'aio_id': aio_id,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
            'curve_name': curve_name,
            'curve_index': curve_index,
        }
        inputbox = lambda aio_id, treatment_index, curve_type, curve_name, curve_index, param_name, param_index: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'inputbox',
            'aio_id': aio_id,
            'curve_name': curve_name,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
            'curve_index': curve_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        plot = lambda aio_id, treatment_index, curve_type: {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'plot',
            'aio_id': aio_id,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
        }
        store = lambda aio_id, treatment_index, curve_type : {  # noqa
            'component': 'TreatmentCurveSelector',
            'subcomponent': 'store',
            'aio_id': aio_id,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
        }

    ids = _IDs

    def __init__(
            self,
            curves: list[Curve],
            treatment_index: int,
            curve_type: str,
            aio_id: str | dict[str, Any] | None = None,
    ) -> None:
        """Initializes a TreatmentCurveSelector instance."""
        # AIO
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        id_vars = {
            'aio_id': aio_id,
            'treatment_index': treatment_index,
            'curve_type': curve_type,
        }
        # SIGNAL NAME DROPDOWN
        curve_names = [curve.name for curve in curves]
        dropdown = dcc.Dropdown(
            id=self.ids.dropdown(**id_vars),
            options=curve_names,
        )
        children = [dropdown]
        # PARAMETERS LOOP
        for curve_index, curve in enumerate(curves):
            collapse = dbc.Collapse([], id=self.ids.collapse(**id_vars, curve_name=curve.name, curve_index=curve_index))
            children.append(collapse)
            for param_index, param in enumerate(curve.params):
                # INPUTBOX
                inputbox_id = self.ids.inputbox(
                    **id_vars,
                    curve_name=curve.name,
                    curve_index=curve_index,
                    param_name=param.name,
                    param_index=param_index,
                )
                param_inputbox = dbc.InputGroup([
                    dbc.InputGroupText(param.name),
                    dbc.Input(id=inputbox_id, type='number', autofocus=True, **param.to_dict()),
                ], class_name='numeric-input-group')
                collapse.children.append(param_inputbox)
        # GRAPH
        plot = dcc.Graph(id=self.ids.plot(**id_vars))
        children.append(plot)
        # STORE
        param_store = dcc.Store(id=self.ids.store(**id_vars), data={})
        children.append(param_store)
        # INIT CALL
        super().__init__(children=children)

    @staticmethod
    @callback(
        Output(ids.collapse(MATCH, MATCH, MATCH, ALL, ALL), 'is_open'),
        Input(ids.dropdown(MATCH, MATCH, MATCH), 'value'),
        State(ids.dropdown(MATCH, MATCH, MATCH), 'options'),
    )
    def change_curve_params(
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> list[bool]:
        if not dropdown_value:
            return [False] * len(callback_context.outputs_list)
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        return [
            True
            if output['id']['curve_index'] == dropdown_index
            else False
            for output in callback_context.outputs_list
        ]

    @staticmethod
    @callback(
        Output(ids.store(MATCH, MATCH, MATCH), 'data'),
        Input(ids.inputbox(MATCH, MATCH, MATCH, ALL, ALL, ALL, ALL), 'value'),
        Input(ids.dropdown(MATCH, MATCH, MATCH), 'value'),
        State(ids.dropdown(MATCH, MATCH, MATCH), 'options'),
        State(ids.store(MATCH, MATCH, MATCH), 'data'),
    )
    def update_params_store(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
            __: dict[str, str | float] | None,  # doesn't really matter since we will overwrite the dictionary
    ) -> dict[str, str | float] | None:
        if not dropdown_value:
            return None
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        return TreatmentCurveSelector.get_curve_params(
            params=callback_context.inputs_list[0],
            dropdown_value=dropdown_value,
            dropdown_index=dropdown_index,
        )

    @staticmethod
    @callback(
        Output(ids.plot(MATCH, MATCH, MATCH), 'figure'),
        Input(ids.inputbox(MATCH, MATCH, MATCH, ALL, ALL, ALL, ALL), 'value'),
        Input(ids.dropdown(MATCH, MATCH, MATCH), 'value'),
        State(ids.dropdown(MATCH, MATCH, MATCH), 'options'),
    )
    def draw_curve(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> go.Figure:
        if not dropdown_value:
            fig = go.Figure()
        else:
            dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
            curve_params = TreatmentCurveSelector.get_curve_params(
                params=callback_context.inputs_list[0],
                dropdown_value=dropdown_value,
                dropdown_index=dropdown_index,
            )
            fig = draw_treatment_curve(curve_params=curve_params, curve_type='division')
        return fig

    @staticmethod
    def get_curve_params(
            params: list[dict],
            dropdown_value: str,
            dropdown_index: int,
    ) -> dict[str, str | float]:
        """Returns the parameters of the selected signal."""
        curve_params = {'name': dropdown_value.replace(' ', '').replace('-', '')}
        curve_params.update({
            param['id']['param_name'].lower().replace(' ', '_').replace('-', ''): param['value']
            for param in params
            if param['id']['curve_index'] == dropdown_index
        })
        return curve_params
