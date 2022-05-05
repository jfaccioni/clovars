import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0
import QtQuick.Layouts

ColumnLayout {
    property var params  // list of ParamModel instances
    Repeater {
        model: params
//        CheckDoubleSpinBox {
//            label: modelData.name
//            value: modelData.value
//            minimum: modelData.minimum
//            maximum: modelData.maximum
//            step: modelData.step
//            onValueModified: function(value) { modelData.value = value; }
//        }
    ColumnLayout {
//        property string label: 'CheckBox Label'
//        property real value: 50.0
//        property real minimum: 0.0
//        property real maximum: 100.0
//        property real step: 1.0
           CheckBox {
                id: checkbox
                checked: false
                text: modelData.name
           }
           DoubleSpinBox {
                editable: true
                dValue: modelData.value
                dFrom: model.Dataminimum
                dTo: modelData.maximum
                dStepSize: modelData.step
                onValueModified: modelData.value = value
                enabled: checkbox.checked
            }
        }
    }
}
