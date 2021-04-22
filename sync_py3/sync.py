#!/usr/bin/env python
"""
sync.py

Allen Instute of Brain Science

created on Oct 10 2014

@author: derricw

"""

import datetime
import time

import h5py as h5
import numpy as np

from toolbox.IO.nidaq import (
    EventInput,
    CounterInputU32,
    CounterInputU64,
    CounterOutputFreq,
    DigitalInput,
)
from toolbox.misc.timer import timeit
from .dataset import Dataset

sync_version = 1.0


class Sync(object):
    """
    Sets up a combination of a single EventInput, counter input/
        output pair to record IO events in a compact binary file.

    Parameters
    ----------
    device : str
        NI DAQ Device, ex: 'Dev1'
    counter_input : str
        NI Counter terminal, ex: 'ctr0'
    counter_output : str
        NI Counter terminal, ex: 'ctr0'
    output_path : str
        Output file path, optional
    event_bits : int (32)
        Event Input bits
    counter_bits : int (32)
        32 or 64
    freq : float (100000.0)
        Pulse generator frequency
    verbose : bool (False)
        Verbose mode prints a lot of stuff.


    Example
    -------
    >>> from sync import Sync
    >>> import time
    >>> s = Sync('Dev1','ctr0','ctr2,'C:/output.sync', freq=100000.0)
    >>> s.start()
    >>> time.sleep(5)  # collect events for 5 seconds
    >>> s.stop()  # can be restarted
    >>> s.clear()  # cannot be restarted

    """

    def __init__(
        self,
        device,
        counter_input,
        counter_output,
        output_path,
        event_bits=32,
        counter_bits=32,
        freq=100000.0,
        verbose=False,
        force_sync_callback=False,
    ):

        self.device = device
        self.counter_input = counter_input
        self.counter_output = counter_output
        self.counter_bits = counter_bits
        self.output_path = output_path
        self.event_bits = event_bits
        self.freq = freq
        self.verbose = verbose

        # Configure input counter
        if self.counter_bits == 32:
            self.ci = CounterInputU32(device=device, counter=counter_input)
            callback = self._EventCallback32bit
        elif self.counter_bits == 64:
            self.ci = CounterInputU64(device=device, lsb_counter=counter_input,)
            callback = self._EventCallback64bit
        else:
            raise ValueError("Counter can only be 32 or 64 bits.")

        output_terminal_str = "Ctr%sInternalOutput" % counter_output[-1]
        self.ci.setCountEdgesTerminal(output_terminal_str)

        # Configure Pulse Generator
        if self.verbose:
            print(("Counter input terminal", self.ci.getCountEdgesTerminal()))

        self.co = CounterOutputFreq(
            device=device,
            counter=counter_output,
            init_delay=0.0,
            freq=freq,
            duty_cycle=0.50,
        )

        if self.verbose:
            print(("Counter output terminal: ", self.co.getPulseTerminal()))

        # Configure Event Input
        self.ei = EventInput(
            device=device,
            bits=self.event_bits,
            buffer_size=200,
            force_synchronous_callback=force_sync_callback,
            buffer_callback=callback,
            timeout=0.01,
        )

        # Configure Optional Counters
        ## TODO: ADD THIS
        self.optional_counters = []

        self.line_labels = ["" for x in range(32)]

        self.bin = open(self.output_path, 'wb')

    def add_counter(self, counter_input):
        """
        Add an extra counter to this dataset.
        """
        pass

    def add_label(self, bit, name):
        self.line_labels[bit] = name

    def start(self):
        """
        Starts all tasks.  They don't necessarily have to all
            start simultaneously.

        """
        self.start_time = str(datetime.datetime.now())  # get a timestamp

        self.ci.start()
        self.co.start()
        self.ei.start()

    def stop(self):
        """
        Stops all tasks.  They can be restarted.
        
        ***This doesn't seem to work sometimes.  I don't know why.***

        #should we just use clear?
        """
        self.ei.stop()
        self.co.stop()
        self.ci.stop()

    def clear(self, out_file=None):
        """
        Clears all tasks.  They cannot be restarted.
        """
        self.ei.clear()
        self.ci.clear()
        self.co.clear()

        self.timeouts = self.ei.timeouts[:]

        self.ei = None
        self.ci = None
        self.co = None

        self.bin.flush()
        time.sleep(0.2)
        self.bin.close()

        self.bin = None

        self.stop_time = str(datetime.datetime.now())

        self._save_hdf5(out_file)

    def _save_hdf5(self, output_file_path=None):
        # save sync data
        if output_file_path:
            filename = output_file_path
        else:
            filename = self.output_path + ".h5"
        data = np.fromfile(self.output_path, dtype=np.uint32)
        if self.counter_bits == 32:
            data = data.reshape(-1, 2)
        else:
            data = data.reshape(-1, 3)
        h5_output = h5.File(filename, 'w')
        h5_output.create_dataset("data", data=data)
        # save meta data
        meta_data = str(self._get_meta_data())
        meta_data_np = np.string_(meta_data)
        h5_output.create_dataset("meta", data=meta_data_np)
        h5_output.close()
        if self.verbose:
            print(("Recorded %i events." % len(data)))
            print(("Metadata: %s" % meta_data))
            print(("Saving to %s" % filename))
            try:
                ds = Dataset(filename)
                ds.stats()
                ds.close()
            except Exception as e:
                print(("Failed to print quick stats: %s" % e))

    def _get_meta_data(self):
        """

        """
        from .dataset import dset_version

        meta_data = {
            'ni_daq': {
                'device': self.device,
                'counter_input': self.counter_input,
                'counter_output': self.counter_output,
                'counter_output_freq': self.freq,
                'event_bits': self.event_bits,
                'counter_bits': self.counter_bits,
            },
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'line_labels': self.line_labels,
            'timeouts': self.timeouts,
            'version': {'dataset': dset_version, 'sync': sync_version,},
        }
        return meta_data

    # @timeit
    def _EventCallback32bit(self, data):
        """
        Callback for change event.

        Writing is already buffered by open().  OS handles it.
        """
        self.bin.write(np.ctypeslib.as_array(self.ci.read()))
        self.bin.write(np.ctypeslib.as_array(data))

    # @timeit
    def _EventCallback64bit(self, data):
        """
        Callback for change event for 64-bit counter.
        """
        (lsb, msb) = self.ci.read()
        self.bin.write(np.ctypeslib.as_array(lsb))
        self.bin.write(np.ctypeslib.as_array(msb))
        self.bin.write(np.ctypeslib.as_array(data))


if __name__ == "__main__":

    import signal
    import argparse
    import sys

    from PyQt4 import QtCore

    description = """

    sync.py\n

    This program creates a process that controls three NIDAQmx tasks.\n

    1) An event input task monitors all digital lines for rising or falling
        edges.\n
    2) A pulse generator task creates a timebase for the events.\n
    3) A counter counts pulses on the timebase.\n

    """

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("output_path", type=str, help="output data path")
    parser.add_argument(
        "-d", "--device", type=str, help="NIDAQ Device to use.", default="Dev1"
    )
    parser.add_argument(
        "-c",
        "--counter_bits",
        type=int,
        default=64,
        help="Counter timebase bits.",
    )
    parser.add_argument(
        "-b",
        "--event_bits",
        type=int,
        default=32,
        help="Change detection bits.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Print a bunch of crap.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force synchronous callbacks.",
    )
    parser.add_argument(
        "-hz",
        "--frequency",
        type=float,
        default=10000000.0,
        help="Pulse (timebase) frequency.",
    )

    args = parser.parse_args()

    output_path = args.output_path
    force_sync_callback = args.force
    device = args.device
    counter_bits = args.counter_bits
    event_bits = args.event_bits
    verbose = args.verbose
    freq = args.frequency

    print("Starting task...")

    # print(args.__dict__)

    if force_sync_callback:

        """
        Using the force_sync_callback option in NIDAQmx.  Have to create a
            thread to handle the sync object or it will lock up this thread
            when signal gets fast.

        """

        class SyncObject(QtCore.QObject):
            """
                Thread for sync control.  We use Qt because it has a really
                nice event loop.
            """

            cleared = QtCore.pyqtSignal()

            def __init__(self, parent=None, params={}):
                QtCore.QObject.__init__(self, parent)
                self.params = params

            def start(self):
                # create Sync objects
                self.sync = Sync(
                    device,
                    "ctr0",
                    "ctr2",
                    output_path,
                    counter_bits=counter_bits,
                    event_bits=event_bits,
                    freq=freq,
                    verbose=verbose,
                    force_sync_callback=True,
                )

                self.sync.start()

            def clear(self):
                self.sync.clear()
                print("Cleared...")
                self.cleared.emit()

        app = QtCore.QCoreApplication(sys.argv)

        s_obj = SyncObject()
        s_thr = QtCore.QThread()

        s_obj.moveToThread(s_thr)
        s_thr.start()
        s_thr.setPriority(QtCore.QThread.TimeCriticalPriority)

        # starts sync object within thread
        QtCore.QTimer.singleShot(100, s_obj.start)

        timer = QtCore.QTimer()
        timer.start(500)
        # check for python signals every 500ms
        timer.timeout.connect(lambda: None)

        def sigint_handler(*args):
            print("Shutting down...")
            QtCore.QTimer.singleShot(100, s_obj.clear)

        def finished(*args):
            s_thr.terminate()
            QtCore.QCoreApplication.quit()

        s_obj.cleared.connect(finished)

        signal.signal(signal.SIGINT, sigint_handler)

        sys.exit(app.exec_())

    else:

        """
            In this mode, NIDAQmx creates and handles its own threading.
            It is unclear how/if this is better.
        """
        sync = Sync(
            device,
            "ctr0",
            "ctr2",
            counter_bits=counter_bits,
            event_bits=event_bits,
            freq=freq,
            output_path=output_path,
            verbose=verbose,
            force_sync_callback=False,
        )

        def signal_handler(signal, frame):
            sync.clear()
            print('Shutting down...')
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        sync.start()

        while True:
            time.sleep(1)
