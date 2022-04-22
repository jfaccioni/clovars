import sys

from PySide6 import QtGui as qtg, QtQml as qtqml


def mainloop(qml_path: str) -> None:
    """Main event loop - displays the signalWidget."""
    app = qtg.QGuiApplication(sys.argv)
    window = qtqml.QQmlApplicationEngine(qml_path)
    sys.exit(app.exec())


if __name__ == '__main__':
    mainloop(qml_path='SignalWidget.qml')
