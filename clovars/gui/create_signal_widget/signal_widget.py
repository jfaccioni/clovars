import sys

from PySide6 import QtGui as qtg, QtQml as qtqml

from gui.create_signal_widget.model import ModelManager


def mainloop(qml_path: str) -> None:
    """Main event loop - displays the signalWidget."""
    app = qtg.QGuiApplication(sys.argv)
    engine = qtqml.QQmlApplicationEngine()
    mm = ModelManager()
    engine.rootContext().setContextProperty("modelNames", mm.names)
    engine.rootContext().setContextProperty("models", mm.models)
    engine.quit.connect(app.quit)  # noqa
    engine.load(qml_path)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == '__main__':
    mainloop(qml_path='SignalWidget.qml')
