import QtQuick
import QtQuick.Controls
import Qt.labs.qmlmodels

ApplicationWindow{
    width: 600
    height: 500
    visible: true

    ComboBox {
        id: combobox
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
    }
    HorizontalHeaderView {
        id: headerView
        syncView: tableView
        contentWidth: 50
        anchors.horizontalCenter: tableView.horizontalCenter
        anchors.top: combobox.bottom
        anchors.topMargin: 30
    }
    TableView {
        id: tableView
        width: 500
        height: 200
        columnSpacing: 5
        rowSpacing: 10
        boundsBehavior: Flickable.StopAtBounds
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: headerView.bottom
        anchors.topMargin: 10
        topMargin: headerView.implicitHeight
        columnWidthProvider: function (column) { return 150 }

        model: signalModel
        delegate: DelegateChooser {
            DelegateChoice {
                column: 0
                delegate: CheckBox {
                    checked: model.edit
                    onToggled: model.edit = checked
                }
            }
            DelegateChoice {
                column: 1
                delegate: Text {
                    text: model.display
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    }
                }
            DelegateChoice {
                column: 2
                delegate: DoubleSpinBox {
                    value: model.display
                    onValueModified: model.display = value
                }
            }
         }
    }
}