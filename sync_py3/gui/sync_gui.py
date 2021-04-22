'''
Created on Oct 18, 2014

@author: derricw
'''


import sys
import os
import datetime
import pickle as pickle

from PyQt4 import QtCore, QtGui

from .sync_gui_layout import Ui_MainWindow
from sync.sync import Sync
from sync.dataset import Dataset

LAST_SESSION = "C:/sync/last.pkl"
DEFAULT_OUTPUT = "C:/sync/output/test"


class MyForm(QtGui.QMainWindow):
    """
    Simple GUI for testing the Sync program.

    Remembers state of all widgets between sessions.

    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._setup_table()
        self._setup_buttons()

        self._load_state()
        self._calculate_rollover()

        self.running = False
        self.sync_thread = None

        self.ui.plainTextEdit.appendPlainText("Ready...")

    def _setup_table(self):
        """
        Sets up the tablewidget so that the numbering is 0:31
        """
        # set vertical labels to 0:31
        labels_int = list(range(32))
        labels_str = [str(i) for i in labels_int]
        self.ui.tableWidget_labels.setVerticalHeaderLabels(labels_str)
        # set horizontal labels
        self.ui.tableWidget_labels.setHorizontalHeaderLabels(['line         '])

    def _setup_buttons(self):
        """
        Setup button callbacks and icons.
        """
        self.ui.pushButton_start.clicked.connect(self._start_stop)
        self.ui.pushButton_start.setIcon(QtGui.QIcon("res/record.png"))
        self.ui.lineEdit_pulse_freq.textChanged.connect(
            self._calculate_rollover
        )
        self.ui.lineEdit_counter_bits.textChanged.connect(
            self._calculate_rollover
        )

    def _start_stop(self):
        """
        Callback for start/stop button press.
        """
        if not self.running:
            # get configuration from gui
            self._start_session()
            self.running = True
            self._disable_ui()
            self.ui.pushButton_start.setIcon(QtGui.QIcon("res/stop.png"))

        else:
            self._stop_session()
            self.running = False
            self._enable_ui()
            self.ui.pushButton_start.setIcon(QtGui.QIcon("res/record.png"))

    def _disable_ui(self):
        """
        Disables the ui.
        """
        self.ui.tableWidget_labels.setEnabled(False)
        self.ui.groupBox.setEnabled(False)

    def _enable_ui(self):
        """
        Enables the UI.
        """
        self.ui.tableWidget_labels.setEnabled(True)
        self.ui.groupBox.setEnabled(True)

    def _start_session(self):
        """
        Starts a session.
        """
        now = datetime.datetime.now()
        self.output_dir = str(self.ui.lineEdit_output_path.text())
        if self.ui.checkBox_timestamp.isChecked():
            self.output_dir += now.strftime('%y%m%d%H%M%S')
        basedir = os.path.dirname(self.output_dir)
        try:
            os.makedirs(basedir)
        except:
            pass
        device = str(self.ui.lineEdit_device.text())
        counter = str(self.ui.lineEdit_counter.text())
        counter_bits = int(self.ui.lineEdit_counter_bits.text())
        if not counter_bits in [32, 64]:
            raise ValueError("Counter must be 64 or 32 bits.")
        data_bits = int(self.ui.lineEdit_data_bits.text())
        pulse = str(self.ui.lineEdit_pulse_out.text())
        freq = float(str(self.ui.lineEdit_pulse_freq.text()))

        # add labels
        labels = self._getLabels()

        # #create Sync object
        params = {
            'device': device,
            'counter': counter,
            'pulse': pulse,
            'output_dir': self.output_dir,
            'counter_bits': counter_bits,
            'event_bits': data_bits,
            'freq': freq,
            'labels': labels,
        }

        self.sync = SyncObject(params=params)
        if self.sync_thread:
            self.sync_thread.terminate()
        self.sync_thread = QtCore.QThread()
        self.sync.moveToThread(self.sync_thread)
        self.sync_thread.start()
        self.sync_thread.setPriority(QtCore.QThread.TimeCriticalPriority)

        QtCore.QTimer.singleShot(100, self.sync.start)

        self.ui.plainTextEdit.appendPlainText(
            "***Starting session at \
            %s on %s ***"
            % (str(now), device)
        )

    def _stop_session(self):
        """
        Ends the session.
        """
        now = datetime.datetime.now()
        # self.sync.clear()
        QtCore.QTimer.singleShot(100, self.sync.clear)
        # self.sync = None

        self.ui.plainTextEdit.appendPlainText(
            "***Ending session at \
            %s ***"
            % str(now)
        )

    def _getLabels(self):
        """
        Gets all of the line labels.
        """
        labels = []
        for i in range(self.ui.tableWidget_labels.rowCount()):
            item = self.ui.tableWidget_labels.item(i, 0)
            if item is not None:
                labels.append(str(item.text()))
            else:
                labels.append("")
        return labels

    def _save_state(self):
        """
        Saves widget states.
        """
        state = {
            'output_dir': str(self.ui.lineEdit_output_path.text()),
            'device': str(self.ui.lineEdit_device.text()),
            'counter': str(self.ui.lineEdit_counter.text()),
            'counter_bits': str(self.ui.lineEdit_counter_bits.text()),
            'event_bits': str(self.ui.lineEdit_data_bits.text()),
            'pulse': str(self.ui.lineEdit_pulse_out.text()),
            'freq': str(self.ui.lineEdit_pulse_freq.text()),
            'labels': self._getLabels(),
            'timestamp': self.ui.checkBox_timestamp.isChecked(),
        }
        with open(LAST_SESSION, 'wb') as f:
            pickle.dump(state, f)

    def _load_state(self):
        """
        Loads previous widget states.
        """
        try:
            with open(LAST_SESSION, 'rb') as f:
                data = pickle.load(f)
            self.ui.lineEdit_output_path.setText(data['output_dir'])
            self.ui.lineEdit_device.setText(data['device'])
            self.ui.lineEdit_counter.setText(data['counter'])
            self.ui.lineEdit_counter_bits.setText(data['counter_bits'])
            self.ui.lineEdit_data_bits.setText(data['event_bits'])
            self.ui.lineEdit_pulse_out.setText(data['pulse'])
            self.ui.lineEdit_pulse_freq.setText(data['freq'])
            self.ui.checkBox_timestamp.setChecked(data['timestamp'])
            for index, label in enumerate(data['labels']):
                self.ui.tableWidget_labels.setItem(
                    index, 0, QtGui.QTableWidgetItem(label)
                )
            self.ui.plainTextEdit.appendPlainText(
                "Loaded previous config successfully."
            )
        except Exception as e:
            print(e)
            self.ui.plainTextEdit.appendPlainText(
                "Couldn't load previous session.  Using defaults."
            )

    def _calculate_rollover(self):
        """
        Calculates the rollover time for the current freqency.
        """
        counter_bits_str = str(self.ui.lineEdit_counter_bits.text())
        if counter_bits_str:
            counter_bits = int(counter_bits_str)
        else:
            return
        if counter_bits == 32:
            freq = float(str(self.ui.lineEdit_pulse_freq.text()))
            try:
                seconds = 4294967295 / freq  # max unsigned
                timestr = str(datetime.timedelta(seconds=seconds))
            except:
                timestr = "???"
        elif counter_bits == 64:
            timestr = "~FOREVER"
        else:
            timestr = "???"
        self.ui.label_rollover.setText(timestr)

    def closeEvent(self, event):
        self._save_state()
        if self.sync_thread:
            self.sync_thread.terminate()


class SyncObject(QtCore.QObject):
    """
        Thread for controlling sync.

        ##TODO: Fix params argument to not be stupid.
    """

    def __init__(self, parent=None, params={}):

        QtCore.QObject.__init__(self, parent)

        self.params = params

    def start(self):
        # create Sync object
        self.sync = Sync(
            self.params['device'],
            self.params['counter'],
            self.params['pulse'],
            self.params['output_dir'],
            counter_bits=self.params['counter_bits'],
            event_bits=self.params['event_bits'],
            freq=self.params['freq'],
            verbose=True,
            force_sync_callback=False,
        )

        for i, label in enumerate(self.params['labels']):
            self.sync.add_label(i, label)

        self.sync.start()

    def clear(self):
        self.sync.clear()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
