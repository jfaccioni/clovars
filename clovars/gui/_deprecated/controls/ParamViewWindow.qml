import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts

Window {
    visible: true
    width: 180
    height: 180
    ColumnLayout {
        ParamView {
        paramModel: model
        }
        Button {
            text: 'Print Param'
            onClicked: model.print()
        }
    }
}
