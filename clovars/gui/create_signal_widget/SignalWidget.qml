import QtQuick
import QtQuick.Controls
import QtQuick.Controls.GroupBox

Window {
    width: 600
    height: 500
    visible: true

    GroupBox {
        title: 'Add signal disturbance?'
        checkable: true

        Text {
            text: 'Current Signal'
        }

    }
}
