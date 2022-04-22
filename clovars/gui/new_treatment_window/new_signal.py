import sys

from PySide6 import QtGui as qtg, QtQml as qtq

from gui.new_treatment_window.signal_models import MODELS


def main() -> None:
    """Main function of this script."""
    app = qtg.QGuiApplication(sys.argv)
    engine = qtq.QQmlApplicationEngine()
    engine.rootContext().setContextProperty("signalModel", MODELS[2])
    engine.quit.connect(app.quit)  # noqa
    engine.load('signalTableWidget.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
