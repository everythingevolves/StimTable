# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sync_gui.ui'
#
# Created: Thu Nov 13 13:55:31 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)


except AttributeError:

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(844, 543)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEdit_counter_bits = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_counter_bits.setObjectName(
            _fromUtf8("lineEdit_counter_bits")
        )
        self.gridLayout.addWidget(self.lineEdit_counter_bits, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_output_path = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_output_path.setObjectName(
            _fromUtf8("lineEdit_output_path")
        )
        self.gridLayout.addWidget(self.lineEdit_output_path, 0, 1, 1, 1)
        self.checkBox_timestamp = QtGui.QCheckBox(self.groupBox)
        self.checkBox_timestamp.setChecked(True)
        self.checkBox_timestamp.setObjectName(_fromUtf8("checkBox_timestamp"))
        self.gridLayout.addWidget(self.checkBox_timestamp, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.lineEdit_pulse_freq = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_pulse_freq.setObjectName(_fromUtf8("lineEdit_pulse_freq"))
        self.gridLayout.addWidget(self.lineEdit_pulse_freq, 3, 1, 1, 1)
        self.label_rollover = QtGui.QLabel(self.groupBox)
        self.label_rollover.setObjectName(_fromUtf8("label_rollover"))
        self.gridLayout.addWidget(self.label_rollover, 3, 2, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.lineEdit_device = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_device.setObjectName(_fromUtf8("lineEdit_device"))
        self.gridLayout.addWidget(self.lineEdit_device, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.lineEdit_counter = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_counter.setObjectName(_fromUtf8("lineEdit_counter"))
        self.gridLayout.addWidget(self.lineEdit_counter, 5, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 6, 0, 1, 1)
        self.lineEdit_pulse_out = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_pulse_out.setObjectName(_fromUtf8("lineEdit_pulse_out"))
        self.gridLayout.addWidget(self.lineEdit_pulse_out, 6, 1, 1, 1)
        self.checkBox_aux_counter = QtGui.QCheckBox(self.groupBox)
        self.checkBox_aux_counter.setEnabled(False)
        self.checkBox_aux_counter.setObjectName(
            _fromUtf8("checkBox_aux_counter")
        )
        self.gridLayout.addWidget(self.checkBox_aux_counter, 7, 0, 1, 1)
        self.lineEdit_aux_counter = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_aux_counter.setEnabled(False)
        self.lineEdit_aux_counter.setObjectName(
            _fromUtf8("lineEdit_aux_counter")
        )
        self.gridLayout.addWidget(self.lineEdit_aux_counter, 7, 1, 1, 1)
        self.label_data_bits = QtGui.QLabel(self.groupBox)
        self.label_data_bits.setObjectName(_fromUtf8("label_data_bits"))
        self.gridLayout.addWidget(self.label_data_bits, 2, 0, 1, 1)
        self.lineEdit_data_bits = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_data_bits.setObjectName(_fromUtf8("lineEdit_data_bits"))
        self.gridLayout.addWidget(self.lineEdit_data_bits, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)
        self.pushButton_start = QtGui.QPushButton(self.centralwidget)
        self.pushButton_start.setMinimumSize(QtCore.QSize(200, 150))
        self.pushButton_start.setText(_fromUtf8(""))
        self.pushButton_start.setIconSize(QtCore.QSize(128, 128))
        self.pushButton_start.setObjectName(_fromUtf8("pushButton_start"))
        self.gridLayout_2.addWidget(self.pushButton_start, 1, 1, 1, 1)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout_2.addWidget(self.plainTextEdit, 2, 1, 1, 1)
        self.tableWidget_labels = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget_labels.setMinimumSize(QtCore.QSize(150, 0))
        self.tableWidget_labels.setMaximumSize(QtCore.QSize(200, 16777215))
        self.tableWidget_labels.setShowGrid(True)
        self.tableWidget_labels.setGridStyle(QtCore.Qt.DashDotLine)
        self.tableWidget_labels.setCornerButtonEnabled(True)
        self.tableWidget_labels.setRowCount(32)
        self.tableWidget_labels.setColumnCount(1)
        self.tableWidget_labels.setObjectName(_fromUtf8("tableWidget_labels"))
        self.tableWidget_labels.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget_labels.verticalHeader().setDefaultSectionSize(30)
        self.gridLayout_2.addWidget(self.tableWidget_labels, 0, 0, 3, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 844, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Sync", None))
        self.groupBox.setTitle(_translate("MainWindow", "Setup", None))
        self.lineEdit_counter_bits.setText(_translate("MainWindow", "64", None))
        self.label_6.setText(_translate("MainWindow", "Counter Bits", None))
        self.label.setText(_translate("MainWindow", "Output path:", None))
        self.lineEdit_output_path.setText(
            _translate("MainWindow", "C:/sync/output/test", None)
        )
        self.checkBox_timestamp.setText(
            _translate("MainWindow", "Timestamp", None)
        )
        self.label_2.setText(_translate("MainWindow", "Pulse Freq (Hz):", None))
        self.lineEdit_pulse_freq.setText(
            _translate("MainWindow", "100000.0", None)
        )
        self.label_rollover.setText(_translate("MainWindow", "Rollover", None))
        self.label_5.setText(_translate("MainWindow", "Device:", None))
        self.lineEdit_device.setText(_translate("MainWindow", "Dev1", None))
        self.label_4.setText(_translate("MainWindow", "Counter:", None))
        self.lineEdit_counter.setText(_translate("MainWindow", "ctr0", None))
        self.label_3.setText(_translate("MainWindow", "Pulse Out:", None))
        self.lineEdit_pulse_out.setText(_translate("MainWindow", "ctr2", None))
        self.checkBox_aux_counter.setText(
            _translate("MainWindow", "Aux Counter", None)
        )
        self.label_data_bits.setText(
            _translate("MainWindow", "Data Bits", None)
        )
        self.lineEdit_data_bits.setText(_translate("MainWindow", "32", None))
