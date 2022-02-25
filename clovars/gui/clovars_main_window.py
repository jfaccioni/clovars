from __future__ import annotations

import sys

import toml
from PyQt5 import QtGui as qtg, QtWidgets as qtw

from clovars import DEFAULT_ANALYSIS_PATH, DEFAULT_COLONIES_PATH, DEFAULT_RUN_PATH, DEFAULT_VIEW_PATH
from clovars.main import format_analysis_settings, format_run_settings, format_view_settings
from clovars.simulation import analyse_simulation_function, run_simulation_function, view_simulation_function


class CellSimMainWindow(qtw.QMainWindow):
    def __init__(
            self,
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes the CellSimMainWindow."""
        super().__init__(parent=parent)
        self.setMinimumSize(640, 320)
        self.tabs = qtw.QTabWidget()
        self.setCentralWidget(self.tabs)

        # RUN TAB
        self.run_tab = qtw.QWidget()
        self.tabs.addTab(self.run_tab, 'Run')
        self.run_tab.setLayout(qtw.QVBoxLayout())
        with open(DEFAULT_RUN_PATH) as f:
            self.run_widget = TextEditWidget(label='Run settings', text=f.read())
            self.run_tab.layout().addWidget(self.run_widget)
        with open(DEFAULT_COLONIES_PATH) as f:
            self.colonies_widget = TextEditWidget(label='Colonies', text=f.read())
            self.run_tab.layout().addWidget(self.colonies_widget)
        self.run_button = qtw.QPushButton(text='Run')
        self.run_button.clicked.connect(self.run_clovars)  # noqa
        self.run_tab.layout().addWidget(self.run_button)

        # VIEW TAB
        self.view_tab = qtw.QWidget()
        self.tabs.addTab(self.view_tab, 'View')
        self.view_tab.setLayout(qtw.QVBoxLayout())
        with open(DEFAULT_VIEW_PATH) as f:
            self.view_widget = TextEditWidget(label='View settings', text=f.read())
            self.view_tab.layout().addWidget(self.view_widget)
        self.view_button = qtw.QPushButton(text='View')
        self.view_button.clicked.connect(self.view_clovars)  # noqa
        self.view_tab.layout().addWidget(self.view_button)

        # ANALYSIS TAB
        self.analysis_tab = qtw.QWidget()
        self.tabs.addTab(self.analysis_tab, 'Analysis')
        self.analysis_tab.setLayout(qtw.QVBoxLayout())
        with open(DEFAULT_ANALYSIS_PATH) as f:
            self.analysis_widget = TextEditWidget(label='Analysis settings', text=f.read())
            self.analysis_tab.layout().addWidget(self.analysis_widget)
        self.analysis_button = qtw.QPushButton(text='Analyse')
        self.analysis_button.clicked.connect(self.analyse_clovars)  # noqa
        self.analysis_tab.layout().addWidget(self.analysis_button)

    def run_clovars(self) -> None:
        """Runs CloVarS with the current settings on display."""
        run_settings = format_run_settings(
            run_settings=toml.loads(self.run_widget.get_plain_text()),  # noqa
            colony_data=toml.loads(self.colonies_widget.get_plain_text()),  # noqa
        )
        run_simulation_function(**run_settings)

    def view_clovars(self) -> None:
        """Views CloVarS with the current settings on display."""
        view_settings = format_view_settings(
            view_settings=toml.loads(self.view_widget.get_plain_text()),  # noqa
        )
        view_simulation_function(**view_settings)

    def analyse_clovars(self) -> None:
        """Analyses CloVarS with the current settings on display."""
        analysis_settings = format_analysis_settings(
            analysis_settings=toml.loads(self.analysis_widget.get_plain_text()),  # noqa
        )
        analyse_simulation_function(**analysis_settings)


class TextEditWidget(qtw.QWidget):
    """Class representing a text edit widget with a label on the top."""
    def __init__(
            self,
            label: str = '',
            text: str = '',
            parent: qtw.QWidget | None = None,
    ) -> None:
        """Initializes a ModeWidget instance."""
        super().__init__(parent=parent)

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.label = qtw.QLabel(text=label)
        layout.addWidget(self.label)
        self.text_edit = qtw.QPlainTextEdit(plainText=text)  # noqa
        self.text_edit.setWordWrapMode(qtg.QTextOption.NoWrap)
        layout.addWidget(self.text_edit)

    def get_plain_text(self) -> str:
        """Returns the text on the underlying QPlainTextEdit widget."""
        return self.text_edit.toPlainText()


def mainloop() -> None:
    """Executes the main loop on the GUI."""
    app = qtw.QApplication(sys.argv)
    main_window = CellSimMainWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    mainloop()
