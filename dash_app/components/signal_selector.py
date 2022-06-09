from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.cell_signals import draw_signal
from dash_app.utils import get_dropdown_index

if TYPE_CHECKING:
    import plotly.graph_objs as go
    from dash_app.cell_signals import Signal


class SignalSelector(dbc.Container):
    class _IDs:
        dropdown = lambda aio_id: {  # noqa
            'component': 'SignalSelector',
            'subcomponent': 'dropdown',
            'aio_id': aio_id,
        }
        collapse = lambda aio_id, signal_name, signal_index: {  # noqa
            'component': 'SignalSelector',
            'subcomponent': 'inputgroup',
            'aio_id': aio_id,
            'signal_name': signal_name,
            'signal_index': signal_index,
        }
        inputbox = lambda aio_id, signal_name, signal_index, param_name, param_index: {  # noqa
            'component': 'SignalSelector',
            'subcomponent': 'inputbox',
            'aio_id': aio_id,
            'signal_name': signal_name,
            'signal_index': signal_index,
            'param_name': param_name,
            'param_index': param_index,
        }
        plot = lambda aio_id: {  # noqa
            'component': 'SignalSelector',
            'subcomponent': 'plot',
            'aio_id': aio_id,
        }
        store = lambda aio_id : {  # noqa
            'component': 'SignalSelector',
            'subcomponent': 'store',
            'aio_id': aio_id,
        }

    ids = _IDs

    def __init__(
            self,
            signals: list[Signal],
            aio_id: str | None = None,
    ) -> None:
        """Initializes a SignalSelector instance."""
        # AIO
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        # SIGNAL NAME DROPDOWN
        signal_names = [signal.name for signal in signals]
        dropdown = dcc.Dropdown(
            id=self.ids.dropdown(aio_id=aio_id),
            options=signal_names,
        )
        children = [dropdown]
        # PARAMETERS LOOP
        for signal_index, signal in enumerate(signals):
            collapse = dbc.Collapse([], id=self.ids.collapse(aio_id, signal.name, signal_index))
            children.append(collapse)
            for param_index, param in enumerate(signal.params):
                # INPUTBOX
                inputbox_id = self.ids.inputbox(aio_id, signal.name, signal_index, param.name, param_index)
                param_inputbox = dbc.InputGroup([
                    dbc.InputGroupText(param.name),
                    dbc.Input(id=inputbox_id, type='number', autofocus=True, **param.to_dict()),
                ], class_name='numeric-input-group')
                collapse.children.append(param_inputbox)
        # GRAPH
        plot = dcc.Graph(id=self.ids.plot(aio_id=aio_id))
        children.append(plot)
        # STORE
        param_store = dcc.Store(id=self.ids.store(aio_id=aio_id), data={})
        children.append(param_store)
        # INIT CALL
        super().__init__(children=children)

    @staticmethod
    @callback(
        Output(ids.collapse(MATCH, ALL, ALL), 'is_open'),
        Input(ids.dropdown(MATCH), 'value'),
        State(ids.dropdown(MATCH), 'options'),
    )
    def change_signal_params(
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> list[bool]:
        if not dropdown_value:
            return [False] * len(callback_context.outputs_list)
        dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
        return [
            True
            if output['id']['signal_index'] == dropdown_index
            else False
            for output in callback_context.outputs_list
        ]

    @staticmethod
    @callback(
        Output(ids.store(MATCH), 'data'),
        Input(ids.inputbox(MATCH, ALL, ALL, ALL, ALL), 'value'),
        Input(ids.dropdown(MATCH), 'value'),
        State(ids.dropdown(MATCH), 'options'),
        State(ids.store(MATCH), 'data'),
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
        return SignalSelector.get_signal_params(
            params=callback_context.inputs_list[0],
            dropdown_value=dropdown_value,
            dropdown_index=dropdown_index,
        )

    @staticmethod
    @callback(
        Output(ids.plot(MATCH), 'figure'),
        Input(ids.inputbox(MATCH, ALL, ALL, ALL, ALL), 'value'),
        Input(ids.dropdown(MATCH), 'value'),
        State(ids.dropdown(MATCH), 'options'),
    )
    def draw_signal(
            _: list[float | None],  # we want these to trigger the callback, but we do not care about the values
            dropdown_value: str | None,
            dropdown_options: list[str],
    ) -> go.Figure:
        if not dropdown_value:
            fig = px.line()
        else:
            dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
            signal_params = SignalSelector.get_signal_params(
                params=callback_context.inputs_list[0],
                dropdown_value=dropdown_value,
                dropdown_index=dropdown_index,
            )
            fig = draw_signal(signal_params=signal_params)
        return fig

    @staticmethod
    def get_signal_params(
            params: list[dict],
            dropdown_value: str,
            dropdown_index: int,
    ) -> dict[str, str | float]:
        """Returns the parameters of the selected signal."""
        signal_params = {'name': dropdown_value.replace(' ', '').replace('-', '')}
        signal_params.update({
            param['id']['param_name'].lower().replace(' ', '_').replace('-', ''): param['value']
            for param in params
            if param['id']['signal_index'] == dropdown_index
        })
        return signal_params
