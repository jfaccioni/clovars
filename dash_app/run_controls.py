from __future__ import annotations

import uuid
from typing import Type, Callable

import dash_bootstrap_components as dbc
from dash import callback, MATCH
from dash.dependencies import Input, Output


def create_id_class(
        component_name: str,
        subcomponent_names: list[str],
) -> Type[_IDs]:  # noqa
    """
    Helper function that creates the "IDs" class to Dash composite components.
    See: https://community.plotly.com/t/composite-components-draft-proposal-pt-2/54965/8
    """
    class _IDs:
        pass

    def create_id_function(subcomponent_name: str) -> Callable:
        def create_id(instance: str | tuple[str, ...]) -> dict[str, str]:
            if isinstance(instance, tuple):
                return {
                    "instance": instance[0],
                    **{f"instance{i}": val for i, val in enumerate(instance[1:], 1)},
                    "component": component_name,
                    "subcomponent": subcomponent_name,
                }
            else:
                return {
                    "instance": instance,
                    "component": component_name,
                    "subcomponent": subcomponent_name,
                }
        return create_id

    for name in subcomponent_names:
        setattr(_IDs, name, create_id_function(name))
    return _IDs


class NumberInputCheckBox(dbc.InputGroup):
    """Class representing an input box activated by a switch, wrapped in an InputGroup."""
    _component_name = __qualname__
    _subcomponent_names = ['checkbox', 'number_input', 'label', 'store']
    ids = create_id_class(component_name=_component_name, subcomponent_names=_subcomponent_names)

    def __init__(
            self,
            start_enabled: bool = False,
            start_label: str = "",
            placeholder_label: str = "",
            end_label: str | None = None,
            start_value: float | None = None,
            min_value: float | None = None,
            max_value: float | None = None,
            step_value: float | None = None,
            uid: str | None = None,
    ) -> None:
        """Initializes a SwitchBox instance."""
        if uid is None:
            uid = str(uuid.uuid4())

        checkbox_properties = {
            'value': start_enabled,
            'label': start_label,
        }
        number_input_properties = {
            'value': start_value,
            'placeholder': placeholder_label,
            'min': min_value,
            'max': max_value,
            'step': step_value,
        }
        label_properties = {
            'children': end_label,
        }

        super().__init__([
            dbc.InputGroupText(dbc.Checkbox(id=self.ids.checkbox(uid), **checkbox_properties)),
            dbc.Input(type='number', id=self.ids.number_input(uid), **number_input_properties),
            dbc.InputGroupText(id=self.ids.label(uid), **label_properties) if end_label is not None else None,
            # dcc.Store(id=self.ids.store(uid), data={'value': None}),
        ])

    @staticmethod
    @callback(
        Output(ids.number_input(MATCH), 'disabled'),
        # Input(ids.number_input(MATCH), 'value'),
        Input(ids.checkbox(MATCH), 'value'),
        # State(ids.store(MATCH), 'data'),
    )
    def set_input_active(
            # number: float,
            switch_is_active: bool,
            # data_store: dict,
    ) -> bool:
        if switch_is_active:  # do not disable number input
            # data_store['value'] = number
            return False
        else:
            # data_store['value'] = None
            return True


# class RunModel(dbc.Card):
#     """Model holding information of the Run (global) parameters."""
#     _component_name = __qualname__
#     _subcomponent_names = ['delta_input', 'frames_input', 'time_label', 'store']
#     ids = create_id_class(component_name=_component_name, subcomponent_names=_subcomponent_names)
#
#     _defaults = {
#         'delta': 3600,
#         'last_frame': 144,
#         'single_colony': 100,
#         'all_colonies': 50,
#     }
#
#     def __init__(
#             self,
#             uid: str | None = None,
#     ) -> None:
#         """Initializes a RunModel."""
#         if uid is None:
#             uid = str(uuid.uuid4())
#
#         super().__init__([
#             dbc.Label('Simulation Parameters', size='lg'),
#             html.Br(),
#             html.Div([
#                 dbc.Label('Delta between frames'),
#                 dbc.InputGroup([
#                     dbc.Input(
#                         type="number",
#                         id=self.ids.delta_input(uid),
#                         value=self._defaults['delta'],
#                         min=0,
#                         step=100,
#                     ),
#                     dbc.InputGroupText('seconds')
#                 ]),
#             ]),
#             html.Br(),
#             html.Div([
#                 dbc.Label('Stop Conditions'),
#                 html.Br(),
#                 NumberInputCheckBox(
#                     start_label='Stop after iterating for',
#                     start_value=self._defaults['last_frame'],
#                     end_label='frames'
#                 ),
#                 html.Br(),
#                 NumberInputCheckBox(
#                     start_label='Stop when a colony reaches',
#                     start_value=self._defaults['single_colony'],
#                     end_label='cells'
#                 ),
#                 html.Br(),
#                 NumberInputCheckBox(
#                     start_label='Stop when all colonies reach',
#                     start_value=self._defaults['all_colonies'],
#                     end_label='cells'
#                 ),
#             ]),
#             html.Br(),
#             html.Div([dbc.Label("", id=self.ids.time_label(uid))]),
#             # dcc.Store(id=self.ids.store(uid), data={'value': None}),
#         ], body=True)
#
#     @staticmethod
#     @callback(
#         Output(ids.time_label(MATCH), 'children'),
#         Input(ids.delta_input(MATCH), 'value'),
#         Input(ids.frames_input(MATCH), 'value'),
#     )
#     def set_total_runtime_label(
#             delta: int,
#             n_frames: int | None,
#     ) -> str:
#         print(delta)
#         print(n_frames)
#         if n_frames is None:
#             return ""
#         else:
#             total_seconds = (delta * n_frames)
#             total_hours = total_seconds / (60 * 60)
#             total_days = total_hours / 24
#             return f"Simulation will run for {round(total_hours, 3)} hours ({round(total_days, 3)} days)"
