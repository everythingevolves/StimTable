"""
sync_device.py

Allen Institute for Brain Science

created on 22 Oct 2014

@author: derricw

Tango device for controlling the sync program.  Creates attributes for
    experiment setup and commands for starting/stopping.

"""

import time
import pickle as pickle
from shutil import copyfile
import os

from PyTango.server import server_run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import DevState, AttrWriteType

from sync import Sync


class SyncDevice(Device, metaclass=DeviceMeta):

    """
    Tango Sync device class.

    Parameters
    ----------
    None

    Examples
    --------

    >>> from PyTango.server import server_run
    >>> server_run((SyncDevice,))

    """

    time = attribute()  # read only is default

    error_handler = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    device = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    counter_input = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    counter_output = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    pulse_freq = attribute(dtype=float, access=AttrWriteType.READ_WRITE,)

    output_path = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    line_labels = attribute(dtype=str, access=AttrWriteType.READ_WRITE,)

    # ------------------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------------------

    def init_device(self):
        """
        Device constructor.  Automatically run by Tango upon device export.
        """
        self.set_state(DevState.ON)
        self.set_status("READY")
        self.attr_error_handler = ""
        self.attr_device = 'Dev1'
        self.attr_counter_input = 'ctr0'
        self.attr_counter_output = 'ctr2'
        self.attr_counter_bits = 64
        self.attr_event_bits = 24
        self.attr_pulse_freq = 10000000.0
        self.attr_output_path = "C:/sync/output/test.h5"
        self.attr_line_labels = "[]"
        print("Device initialized...")

    # ------------------------------------------------------------------------------
    # Attribute R/W
    # ------------------------------------------------------------------------------

    def read_time(self):
        return time.time()

    def read_error_handler(self):
        return self.attr_error_handler

    def write_error_handler(self, data):
        self.attr_error_handler = data

    def read_device(self):
        return self.attr_device

    def write_device(self, data):
        self.attr_device = data

    def read_counter_input(self):
        return self.attr_counter_input

    def write_counter_input(self, data):
        self.attr_counter_input = data

    def read_counter_output(self):
        return self.attr_counter_output

    def write_counter_output(self, data):
        self.attr_counter_output = data

    def read_pulse_freq(self):
        return self.attr_pulse_freq

    def write_pulse_freq(self, data):
        self.attr_pulse_freq = data

    def read_output_path(self):
        return self.attr_output_path

    def write_output_path(self, data):
        self.attr_output_path = data

    def read_line_labels(self):
        return self.attr_line_labels

    def write_line_labels(self, data):
        self.attr_line_labels = data

    # ------------------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------------------

    @command(dtype_in=str, dtype_out=str)
    def echo(self, data):
        """
        For testing. Just echos whatever string you send.
        """
        return data

    @command(dtype_in=str, dtype_out=None)
    def throw(self, msg):
        print(("Raising exception:", msg))
        # Send to error handler or sequencing engine

    @command(dtype_in=None, dtype_out=None)
    def start(self):
        """
        Starts an experiment.
        """
        print("Starting experiment...")

        self.sync = Sync(
            device=self.attr_device,
            counter_input=self.attr_counter_input,
            counter_output=self.attr_counter_output,
            counter_bits=self.attr_counter_bits,
            event_bits=self.attr_event_bits,
            output_path=self.attr_output_path,
            freq=self.attr_pulse_freq,
            verbose=True,
            force_sync_callback=False,
        )

        lines = eval(self.attr_line_labels)
        for index, line in enumerate(lines):
            self.sync.add_label(index, line)

        self.sync.start()

    @command(dtype_in=None, dtype_out=None)
    def stop(self):
        """
        Stops an experiment and clears the NIDAQ tasks.
        """
        print("Stopping experiment...")
        try:
            self.sync.stop()
        except Exception as e:
            print(e)

        self.sync.clear(self.attr_output_path)
        self.sync = None
        del self.sync

    @command(dtype_in=str, dtype_out=None)
    def load_config(self, path):
        """
        Loads a configuration from a .pkl file.
        """
        print(("Loading configuration: %s" % path))

        with open(path, 'rb') as f:
            config = pickle.load(f)

        self.attr_device = config['device']
        self.attr_counter_input = config['counter']
        self.attr_counter_output = config['pulse']
        self.attr_counter_bits = int(config['counter_bits'])
        self.attr_event_bits = int(config['event_bits'])
        self.attr_pulse_freq = float(config['freq'])
        self.attr_output_path = config['output_dir']
        self.attr_line_labels = str(config['labels'])

    @command(dtype_in=str, dtype_out=None)
    def save_config(self, path):
        """
        Saves a configuration to a .pkl file.
        """
        print(("Saving configuration: %s" % path))

        config = {
            'device': self.attr_device,
            'counter': self.attr_counter_input,
            'pulse': self.attr_counter_output,
            'freq': self.attr_pulse_freq,
            'output_dir': self.attr_output_path,
            'labels': eval(self.attr_line_labels),
            'counter_bits': self.attr_counter_bits,
            'event_bits': self.attr_event_bits,
        }

        with open(path, 'wb') as f:
            pickle.dump(config, f)

    @command(dtype_in=str, dtype_out=None)
    def copy_dataset(self, folder):
        """
        Copies last dataset to specified folder.
        """
        source = self.attr_output_path
        dest = os.path.join(folder, os.path.basename(source))

        copyfile(source, dest)


if __name__ == "__main__":
    server_run((SyncDevice,))
