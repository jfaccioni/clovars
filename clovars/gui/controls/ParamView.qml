import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts
import examples.adding.people 1.0


ColumnLayout {
    PyParams {
        id: pyParam
        name: "Some Param"
        value: 2.5
    }
    CheckBox {
        id: checkbox
        text: pyParam.name
        checked: false
        onClicked: checked ? pyParam.value = null: pyParam.value = value
    }
    DoubleSpinBox {
        id: spinbox
        dValue: pyParam.value
        dFrom: pyParam.minimum
        dTo: pyParam.maximum
        dStepSize: pyParam.step
        editable: true
        enabled: checkbox.checked
        onDValueChanged: pyParam.value = dValue
    }
    Button {
        text: "Show value"
        onClicked: console.log(pyParam.value)
    }
}
