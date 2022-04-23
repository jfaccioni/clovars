import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

Window {
    id: mainWindow
    width: 400
    height: 460
    visible: true

    GroupBox {
        id: box
        width: mainWindow.width
        height: mainWindow.height
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.horizontalCenter: parent.horizontalCenter
        label: CheckBox {
            id: groupCheckBox
            checked: false
            text: 'Add signal disturbance?'
        }

        ColumnLayout {
            anchors.fill: parent
            enabled: groupCheckBox.checked
            visible: groupCheckBox.checked

            Text {
                Layout.alignment: Qt.AlignLeft
                text: "Current Signal"
            }

            ComboBox {
                id: currentSignalComboBox
                Layout.alignment: Qt.AlignLeft
                model: modelNames
                onActivated: GroupBox.resize
            }

            StackView {
                id: stackView
                width: box.width
                height: box.height
                Repeater {
                    model: models
                    ColumnLayout {
                        anchors.fill: parent
                    HorizontalHeaderView {
                        syncView: tableView
                        visible: currentSignalComboBox.currentIndex === index
                    }
                    TableView {
                        id: tableView
                        width: stackView.width
                        height: stackView.height
                        visible: currentSignalComboBox.currentIndex === index
                        columnSpacing: 5
                        rowSpacing: 10
                        boundsBehavior: Flickable.StopAtBounds
                        model: modelData
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
                    Button {
                        text: 'Save Signal'
                        onClicked: model.printData
                    }}
                }
            }
        }
    }
}
