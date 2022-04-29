from __future__ import annotations

from PySide6 import QtWidgets as qtw

from clovars.gui.params_manager import ParamsManager


def _add_show_model_button(widget: qtw.QWidget) -> None:
    """Adds a button to the widget's layout, which prints its model (skips if the widget has no layout or model)."""
    try:
        model = widget.model  # noqa
        layout = widget.layout()
    except AttributeError:
        pass
    else:
        debug_button = qtw.QPushButton('Show Model')
        debug_button.clicked.connect(lambda: print(model))  # noqa
        layout.addWidget(debug_button)


def _add_show_value_button(widget: qtw.QWidget) -> None:
    """Adds a button to the widget's layout, which prints the widget's get_value() returned value when clicked."""
    try:
        layout = widget.layout()
    except AttributeError:
        pass
    else:
        debug_button = qtw.QPushButton('Show Value')
        debug_button.clicked.connect(widget.display_value)  # noqa
        layout.addWidget(debug_button)


def _wrap_in_window(widget: qtw.QWidget) -> qtw.QMainWindow:
    """Wraps the widget in a QMainWindow and then returns the window."""
    window = qtw.QMainWindow()
    window.setCentralWidget(widget)
    return window


def _wrap_many_in_window(
        widgets: list[qtw.QWidget],
        orientation: str = 'horizontal',
) -> qtw.QMainWindow:
    """Wraps the widgets in a QMainWindow along the desired orientation, and then returns the window."""
    # Get layout and put widgets inside
    if orientation not in ['horizontal', 'vertical']:
        orientation = 'horizontal'  # default
    layout = qtw.QVBoxLayout() if orientation == 'vertical' else qtw.QHBoxLayout()
    for widget in widgets:
        layout.addWidget(widget)

    window = qtw.QMainWindow()
    w = qtw.QWidget()
    w.setLayout(layout)
    window.setCentralWidget(w)
    return window
