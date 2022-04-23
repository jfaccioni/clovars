import sys

from PySide6 import QtGui as qtg, QtQml as qtqml

from gui.create_signal_widget.model import SignalModelManager


def mainloop(qml_path: str) -> None:
    """Main event loop - displays the signalWidget."""
    app = qtg.QGuiApplication(sys.argv)
    engine = qtqml.QQmlApplicationEngine()
    signal_manager = SignalModelManager()
    engine.rootContext().setContextProperty("signalManager", signal_manager)
    engine.quit.connect(app.quit)  # noqa
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == '__main__':
    mainloop(qml_path='SignalWidget.qml')
