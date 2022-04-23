import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

import "../controls" as MyControls

Window {
    id: mainWindow
    width: 400
    height: 460
    visible: true
    ColumnLayout {
        Layout.margins: 0
        CheckBox {
            id: checkbox
            checked: false
            text: 'Add signal disturbance?'
        }
        RowLayout {
            Layout.margins: 0
            enabled: checkbox.checked
             Text {
                Layout.alignment: Qt.AlignLeft
                text: "Type:"
            }
            ComboBox {
                id: combobox
                Layout.alignment: Qt.AlignLeft
                model: signalManager.signalNames
                onActivated: function(index) { signalManager.signalIndex = index }
            }
        }
        Repeater {
            model: signalManager.signalModels
            MyControls.ParamsColumn {
                Layout.alignment: Qt.AlignLeft
                visible: combobox.currentIndex === index
                enabled: checkbox.checked
                params: modelData.params
            }
        }
        Button {
            text: 'Save'
            onClicked: signalManager.displayModel()
        }
        Item {
        Layout.fillHeight: true
        }
    }
}
