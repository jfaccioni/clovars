from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, callback, Output, Input, MATCH, ALL, callback_context, State

from dash_app.utils import get_dropdown_index
from dash_app.cell_signals import draw_signal

if TYPE_CHECKING:
    from dash.development.base_component import Component
    import plotly.graph_objs as go
    from dash_app.cell_signals import Signal


def NumericInputGroup(
        name: str | dict = "",
        prefix: str = "",
        suffix: str = "",
        with_checkbox: bool = False,
        checked: bool = False,
        value: int | float | None = None,
        min_: int | float | None = None,
        max_: int | float | None = None,
        step: int | float | None = None,
) -> dbc.InputGroup:
    """
    Convenience function that returns an InputGroup with a numeric input box, along with some formatting options.
    The parameters are:

      - name: defines the ID of each element inside the InputGroup (see below).
      - prefix: text that appears in an InputGroupText before / to the left of the Input component.
      - suffix: text that appears in an InputGroupText after / to the right of the Input component.
      - with_checkbox: if True, the prefix InputGroupText includes a Checkbox element.
      - checked: defines the checked state of the Checkbox (does nothing if with_checkbox is False).
      - value/min_/max_/step: passed onto the Input component, defining its limits and single step value.

    The IDs of the internal elements are:
      - inputbox: { 'type': 'numeric-input-inputbox', 'name': <name-parameter> }
      - checkbox (only if with_checkbox=True): { 'type': 'numeric-input-checkbox', 'name': <name-parameter> }
    """
    if not name:
        name = {'name': str(uuid.uuid4())}
    elif isinstance(name, str):
        name = {'name': name}
    numeric_input_params = {
        'value': value or 5,
        'min': min_ or 0,
        'max': max_ or 10,
        'step': step or 1,
    }
    components = []
    # PREFIX
    if with_checkbox is True:
        checkbox_id = {'type': 'numeric-input-checkbox'}
        checkbox_id.update(name)
        components.append(dbc.InputGroupText(dbc.Checkbox(id=checkbox_id, label=prefix or None, value=checked)))
    elif prefix:
        components.append(dbc.InputGroupText(children=prefix))
    # INPUTBOX
    input_id = {'type': 'numeric-input-inputbox'}
    input_id.update(name)
    inputbox = dbc.Input(id=input_id, type="number", autofocus=True, **numeric_input_params)
    components.append(inputbox)
    # SUFFIX
    if suffix:
        components.append(dbc.InputGroupText(children=suffix))
    return dbc.InputGroup(components, class_name="numeric-input-group flex-nowrap")


# ### COMPONENT-SPECIFIC CALLBACKS
@callback(
    Output({'type': 'numeric-input-inputbox', 'name': MATCH}, 'disabled'),
    Input({'type': 'numeric-input-checkbox', 'name': MATCH}, 'value'),
)
def set_inputbox_disabled(checkbox_enabled: bool) -> bool:
    """Disables the numeric inputbox whenever the checkbox is unchecked."""
    return not checkbox_enabled


#####


def CollapsableContainer(
        children: list[Component] | None = None,
        name: str = "",
        label: str = "",
        checked: bool = False,
) -> dbc.Container:
    """Returns a Container containing a checkbox that opens/closes a collapsable component."""
    name = name or str(uuid.uuid4())
    checkbox_id = {'type': 'collapsable-div-checkbox', 'name': name}
    collapse_id = {'type': 'collapsable-div-collapse', 'name': name}
    return dbc.Container(
        [
            dbc.Checkbox(id=checkbox_id, label=label or None, value=checked),
            dbc.Collapse(id=collapse_id, children=children or [], is_open=checked)
        ]
    )


# ### COMPONENT-SPECIFIC CALLBACKS
@callback(
    Output({'type': 'collapsable-div-collapse', 'name': MATCH}, 'is_open'),
    Input({'type': 'collapsable-div-checkbox', 'name': MATCH}, 'value'),
)
def toggle_collapsable_container(checkbox_checked: bool) -> bool:
    """Opens/closes the collapsable Container whenever its checkbox is checked."""
    return checkbox_checked


#####


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

# def DivSelectorDropdown(
#         children: dict[str, Component] | None = None,
#         name: str = "",
# ) -> dbc.Container:
#     """Returns a Container containing a selector that displays a given div in the children dictionary."""
#     if children is None:
#         return dbc.Container([])
#     name = name or str(uuid.uuid4())
#     dropdown = dcc.Dropdown(
#         id={'type': 'div-selector-dropdown', 'name': name},
#         options=list(children),
#         className='div-selector-dropdown',
#     )
#     elements = [dropdown]
#     for index, (key, value) in enumerate(children.items()):
#         value.id = {'type': 'div-selector-child', 'parent-label': key, 'name': name}
#         elements.append(value)
#     return dbc.Container(elements)


# ### COMPONENT-SPECIFIC CALLBACKS

# @callback(
#     Output({'type': 'div-selector-child', 'parent-label': ALL, 'name': MATCH}, 'style'),
#     Input({'type': 'div-selector-dropdown', 'name': MATCH}, 'value'),
#     State({'type': 'div-selector-dropdown', 'name': MATCH}, 'options'),
# )
# def change_div_selector_display(
#         dropdown_value: str | None,
#         dropdown_options: list[dict[str, str]],
# ) -> list[dict[str, str]]:
#     values = [{'display': 'none'}] * len(callback_context.outputs_list)
#     if dropdown_value:
#         dropdown_index = get_dropdown_index(dropdown_value=dropdown_value, dropdown_options=dropdown_options)
#         values[dropdown_index] = {'display': 'inline'}
#     return values
#
#
# class ParamsInput:
#     noise_params = {
#         'value': 0.2,
#         'min_': 0.0,
#         'max_': 1.0,
#         'step': 0.05,
#     }
#     period_params = {
#         'value': 3600,
#         'min_': 100,
#         'max_': 1_000_000,
#         'step': 100,
#     }
#     stochastic_weight_params = {
#         'value': 0.2,
#         'min_': 0.0,
#         'max_': 1.0,
#         'step': 0.05,
#     }
#     mean_params = {
#         'value': 0.0,
#         'min_': -10.0,
#         'max_': 10.0,
#         'step': 0.05,
#     }
#     std_params = {
#         'value': 0.05,
#         'min_': 0.0,
#         'max_': 50.0,
#         'step': 0.05,
#     }
#     k_params = {
#         'value': 0.5,
#         'min_': 0.05,
#         'max_': 100.0,
#         'step': 0.05,
#     }
#
#     @classmethod
#     def noise(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "noise" parameter."""
#         return NumericInputGroup(name=name, prefix='Noise', **cls.noise_params)
#
#     @classmethod
#     def period(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "period" parameter."""
#         return NumericInputGroup(name=name, prefix='Period', **cls.period_params)
#
#     @classmethod
#     def stochastic_weight(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "stochastic weight" parameter."""
#         return NumericInputGroup(name=name, prefix='Stochastic weight', **cls.stochastic_weight_params)
#
#     @classmethod
#     def mean(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "mean" parameter."""
#         return NumericInputGroup(name=name, prefix='Mean', **cls.mean_params)
#
#     @classmethod
#     def std(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "std" parameter."""
#         return NumericInputGroup(name=name, prefix='Standard deviation', **cls.std_params)
#
#     @classmethod
#     def k(
#             cls,
#             name: str | dict,
#     ) -> NumericInputGroup:
#         """Returns a NumericInputGroup representing the "K" parameter."""
#         return NumericInputGroup(name=name, prefix='K', **cls.k_params)
#
#
# def get_signal_components(name: str) -> dict[str, dbc.Container]:
#     """Returns a dictionary of the signal components."""
#     return {
#         'Stochastic': dbc.Container(
#             className='signal-param-container',
#             children=[
#                 ParamsInput.noise({'name': name, 'signal-type': 'stoch', 'param-name': 'noise'}),
#             ],
#         ),
#         'Sinusoidal': dbc.Container(
#             className='signal-param-container',
#             children=[
#                 ParamsInput.period({'name': name, 'signal-type': 'sin', 'param-name': 'period'}),
#             ],
#         ),
#         'Stochastic-Sinusoidal': dbc.Container(
#             className='signal-param-container',
#             children=[
#                 ParamsInput.noise({'name': name, 'signal-type': 'stoch-sin', 'param-name': 'noise'}),
#                 ParamsInput.period({'name': name, 'signal-type': 'stoch-sin', 'param-name': 'period'}),
#             ParamsInput.stochastic_weight({'name': name, 'signal-type': 'stoch-sin', 'param-name': 'stoch-weight'}),
#             ],
#         ),
#         'Gaussian': dbc.Container(
#             className='signal-param-container',
#             children=[
#                 ParamsInput.mean({'name': name, 'signal-type': 'gaussian', 'param-name': 'mean'}),
#                 ParamsInput.std({'name': name, 'signal-type': 'gaussian', 'param-name': 'std'}),
#             ],
#         ),
#         'E.M. Gaussian': dbc.Container(
#             className='signal-param-container',
#             children=[
#                 ParamsInput.mean({'name': name, 'signal-type': 'em-gaussian', 'param-name': 'mean'}),
#                 ParamsInput.std({'name': name, 'signal-type': 'em-gaussian', 'param-name': 'std'}),
#                 ParamsInput.k({'name': name, 'signal-type': 'em-gaussian', 'param-name': 'k'}),
#             ],
#         ),
#     }
