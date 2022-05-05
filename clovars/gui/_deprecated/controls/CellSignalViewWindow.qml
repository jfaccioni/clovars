import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts

Window {
    visible: true
    height: 300
    width: 200

ColumnLayout {
    anchors.fill: parent
    Text {
        text: cellSignalModel.name
    }
    ListView {
        width: 20
        height: 180
        model: cellSignalModel
        delegate: ParamView {
            height: 60
            model: model.paramModel
        }
    }
    Button {
        text: 'Print CellSignal'
        onClicked: cellSignalModel.print()
    }
    Item {
        Layout.fillHeight: true
    }
}

}

