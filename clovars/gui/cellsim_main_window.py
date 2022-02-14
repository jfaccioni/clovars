from __future__ import annotations

import pprint
import sys
from pathlib import Path
from typing import Optional

from PyQt5 import QtWidgets as qtw, QtCore as qtc

from clovars.gui import ParamsManager
from clovars.simulation import run_simulation_function, analyse_simulation_function, view_simulation_function


class CellSimMainWindow(qtw.QMainWindow):
    def __init__(
            self,
            parent: Optional[qtw.QWidget] = None,
    ) -> None:
        """Initializes the CellSimMainWindow."""
        super().__init__(parent=parent)

        self.params_manager = ParamsManager()

        self.tabs = qtw.QTabWidget()

        self.run_tab = qtw.QWidget()
        self.tabs.addTab(self.run_tab, 'Run')

        self.view_tab = qtw.QWidget()
        self.tabs.addTab(self.view_tab, 'View')

        self.analyse_tab = qtw.QWidget()
        self.tabs.addTab(self.analyse_tab, 'Analyse')

        self.setCentralWidget(self.tabs)

        # Left DockWidget
        self.load_simulation_widget = qtw.QWidget()
        self.controller_dock = qtw.QDockWidget('Controller')
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, self.controller_dock)

        # MenuBar
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction('Load ...', self.prompt_load_simulation)
        file_menu.addSeparator()
        file_menu.addAction('Quit', self.closeEvent)

    def prompt_load_simulation(self) -> None:
        options = qtw.QFileDialog.DontUseNativeDialog
        query = qtw.QFileDialog.getExistingDirectory(self, 'Select directory with simulation', '', options=options)
        if query:
            path = Path(query)
            self.load_simulation(path=path)

    def load_simulation(
            self,
            path: Path,
    ) -> None:
        print(path)
        print(self.params_manager)
        pprint.pprint(self.params_manager.get_run_params())
        pprint.pprint(self.params_manager.get_view_params())
        pprint.pprint(self.params_manager.get_analysis_params())
        run_simulation_function(**self.params_manager.get_run_params())
        view_simulation_function(**self.params_manager.get_view_params())
        analyse_simulation_function(**self.params_manager.get_analysis_params())


def mainloop() -> None:
    """Executes the main loop on the GUI."""
    app = qtw.QApplication(sys.argv)
    main_window = CellSimMainWindow()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    mainloop()
