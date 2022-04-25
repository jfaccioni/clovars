import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts

ListView {
    model: cellSignalModel
    delegate: ParamView {
        height: 60
        model: model.paramModel
    }
}
