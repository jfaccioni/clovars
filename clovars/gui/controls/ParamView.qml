import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts

ColumnLayout {
    property var paramModel
    CheckBox {
        id: checkbox
        text: model.name
        checked: paramModel.activeState
        onClicked: paramModel.activeState = checkbox.checked
    }
    DoubleSpinBox {
        dValue: paramModel.value
        dFrom: paramModel.minimum
        dTo: paramModel.maximum
        dStepSize:paramModel.step
        editable: true
        enabled: checkbox.checked
        onDValueChanged: paramModel.value = dValue
    }
}
