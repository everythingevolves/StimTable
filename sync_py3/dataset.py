"""
dataset.py

Dataset object for loading and unpacking a sync dataset.

"""
from __future__ import unicode_literals
import datetime
import pprint

import h5py as h5
import numpy as np


dset_version = 1.0


def unpack_uint32(uint32_array, endian='L'):
    """
    Unpacks an array of 32-bit unsigned integers into bits.

    Default is least significant bit first.

    """
    if not uint32_array.dtype == np.uint32:
        raise TypeError("Must be uint32 ndarray.")
    buff = np.getbuffer(uint32_array)
    uint8_array = np.frombuffer(buff, dtype=np.uint8)
    uint8_array = np.fliplr(uint8_array.reshape(-1, 4))
    bits = np.unpackbits(uint8_array).reshape(-1, 32)
    if endian.upper() == 'B':
        bits = np.fliplr(bits)
    return bits


def get_bit(uint_array, bit):
    """
    Returns a bool array for a specific bit in a uint ndarray.
    """
    return np.bitwise_and(uint_array, 2 ** bit).astype(bool).astype(np.uint8)


class Dataset(object):
    """
    A sync dataset.  Contains methods for loading
        and parsing the binary data.

    """

    def __init__(self, path):
        self.load(path)

        self.times = self._process_times()

    def _process_times(self):
        times = self.get_all_events()[:, 0:1].astype(np.int64)

        intervals = np.ediff1d(times, to_begin=0)
        rollovers = np.where(intervals < 0)[0]

        for i in rollovers:
            times[i:] += 4294967296

        return times

    def load(self, path):
        """
        Loads an hdf5 sync dataset.
        """
        self.dfile = h5.File(path, 'r')
        self.meta_data = eval(self.dfile['meta'].value)
        self.line_labels = self.meta_data['line_labels']
        return self.dfile

    def get_bit(self, bit):
        """
        Returns the values for a specific bit.
        """
        return get_bit(self.get_all_bits(), bit)

    def get_line(self, line):
        """
        Returns the values for a specific line.
        """
        bit = self._line_to_bit(line)
        return self.get_bit(bit)

    def get_bit_changes(self, bit):
        """
        Returns the first derivative of a specific bit.
            Data points are 1 on rizing edges and 255 on falling edges.
        """
        bit_array = self.get_bit(bit)
        return np.ediff1d(bit_array, to_begin=0)

    def get_all_bits(self):
        """
        Returns the data for all bits.
        """
        return self.dfile['data'].value[:, -1]

    def get_all_times(self):
        """
        Returns all counter values.
        """
        if self.meta_data['ni_daq']['counter_bits'] == 32:
            return self.get_all_events()[:, 0]
        else:
            """

            #this doesn't work because actually the rollover isn't a pulse
            #it goes high after the first rollover then low after the second

            times = self.get_all_events()[:, 0:2].astype(np.uint64)
            times = times[:, 0] + times[:, 1]*np.uint64(4294967296)
            return times
            """
            return self.times

    def get_all_events(self):
        """
        Returns all counter values and their cooresponding IO state.
        """
        return self.dfile['data'].value

    def get_events_by_bit(self, bit):
        """
        Returns all counter values for transitions (both rising and falling)
            for a specific bit.
        """
        changes = self.get_bit_changes(bit)
        return self.get_all_times()[np.where(changes != 0)]

    def get_events_by_line(self, line):
        """
        Returns all counter values for transitions (both rising and falling)
            for a specific line.
        """
        line = self._line_to_bit(line)
        return self.get_events_by_bit(line)

    def _line_to_bit(self, line):
        """
        Returns the bit for a specified line.  Either line name and number is
            accepted.
        """
        if type(line) is int:
            return line
        elif type(line) is str:
            return self.line_labels.index(line)
        else:
            raise TypeError("Incorrect line type.  Try a str or int.")

    def get_rising_edges(self, line):
        """
        Returns the counter values for the rizing edges for a specific bit.
        """
        bit = self._line_to_bit(line)
        changes = self.get_bit_changes(bit)
        return self.get_all_times()[np.where(changes == 1)]

    def get_falling_edges(self, line):
        """
        Returns the counter values for the falling edges for a specific bit.
        """
        bit = self._line_to_bit(line)
        changes = self.get_bit_changes(bit)
        return self.get_all_times()[np.where(changes == 255)]

    def line_stats(self, line, print_results=True):
        """
        Quick-and-dirty analysis of a bit.

        ##TODO: Split this up into smaller functions.

        """
        # convert to bit
        bit = self._line_to_bit(line)

        # get the bit's data
        bit_data = self.get_bit(bit)
        total_data_points = len(bit_data)

        # get the events
        events = self.get_events_by_bit(bit)
        total_events = len(events)

        # get the rising edges
        rising = self.get_rising_edges(bit)
        total_rising = len(rising)

        # get falling edges
        falling = self.get_falling_edges(bit)
        total_falling = len(falling)

        if total_events <= 0:
            if print_results:
                print(("*" * 70))
                print(("No events on line: %s" % line))
                print(("*" * 70))
            return None
        elif total_events <= 10:
            if print_results:
                print(("*" * 70))
                print(("Sparse events on line: %s" % line))
                print(("Rising: %s" % total_rising))
                print(("Falling: %s" % total_falling))
                print(("*" * 70))
            return {
                'line': line,
                'bit': bit,
                'total_rising': total_rising,
                'total_falling': total_falling,
                'avg_freq': None,
                'duty_cycle': None,
            }
        else:

            # period
            period = self.period(line)

            avg_period = period['avg']
            max_period = period['max']
            min_period = period['min']
            period_sd = period['sd']

            # freq
            avg_freq = self.frequency(line)

            # duty cycle
            duty_cycle = self.duty_cycle(line)

            if print_results:
                print(("*" * 70))

                print(("Quick stats for line: %s" % line))
                print(("Bit: %i" % bit))
                print(("Data points: %i" % total_data_points))
                print(("Total transitions: %i" % total_events))
                print(("Rising edges: %i" % total_rising))
                print(("Falling edges: %i" % total_falling))
                print(("Average period: %s" % avg_period))
                print(("Minimum period: %s" % min_period))
                print(("Max period: %s" % max_period))
                print(("Period SD: %s" % period_sd))
                print(("Average freq: %s" % avg_freq))
                print(("Duty cycle: %s" % duty_cycle))

                print(("*" * 70))

            return {
                'line': line,
                'bit': bit,
                'total_data_points': total_data_points,
                'total_events': total_events,
                'total_rising': total_rising,
                'total_falling': total_falling,
                'avg_period': avg_period,
                'min_period': min_period,
                'max_period': max_period,
                'period_sd': period_sd,
                'avg_freq': avg_freq,
                'duty_cycle': duty_cycle,
            }

    def period(self, line, edge="rising"):
        """
        Returns a dictionary with avg, min, max, and sd of period for a line.
        """
        bit = self._line_to_bit(line)

        if edge.lower() == "rising":
            edges = self.get_rising_edges(bit)
        elif edge.lower() == "falling":
            edges = self.get_falling_edges(bit)

        if len(edges) > 1:

            timebase_freq = self.meta_data['ni_daq']['counter_output_freq']
            avg_period = np.mean(np.ediff1d(edges)) / timebase_freq
            max_period = np.max(np.ediff1d(edges)) / timebase_freq
            min_period = np.min(np.ediff1d(edges)) / timebase_freq
            period_sd = np.std(avg_period)

        else:
            raise IndexError("Not enough edges for period: %i" % len(edges))

        return {
            'avg': avg_period,
            'max': max_period,
            'min': min_period,
            'sd': period_sd,
        }

    def frequency(self, line, edge="rising"):
        """
        Returns the average frequency of a line.
        """

        period = self.period(line, edge)
        return 1.0 / period['avg']

    def duty_cycle(self, line):
        """
        Doesn't work right now.  Freezes python for some reason.

        Returns the duty cycle of a line.

        """
        raise NotImplementedError

        bit = self._line_to_bit(line)

        rising = self.get_rising_edges(bit)
        falling = self.get_falling_edges(bit)

        total_rising = len(rising)
        total_falling = len(falling)

        if total_rising > total_falling:
            rising = rising[:total_falling]
        elif total_rising < total_falling:
            falling = falling[:total_rising]
        else:
            pass

        if rising[0] < falling[0]:
            # line starts low
            high = falling - rising
        else:
            # line starts high
            high = np.concatenate(
                falling, self.get_all_events()[-1, 0]
            ) - np.concatenate(0, rising)

        total_high_time = np.sum(high)
        all_events = self.get_events_by_bit(bit)
        total_time = all_events[-1] - all_events[0]
        return 1.0 * total_high_time / total_time

    def stats(self):
        """
        Quick-and-dirty analysis of all bits.  Prints a few things about each
            bit where events are found.
        """
        bits = []
        for i in range(32):
            bits.append(self.line_stats(i, print_results=False))
        active_bits = [x for x in bits if x is not None]
        print(("Active bits: ", len(active_bits)))
        for bit in active_bits:
            print(("*" * 70))
            print(("Bit: %i" % bit['bit']))
            print(("Label: %s" % self.line_labels[bit['bit']]))
            print(("Rising edges: %i" % bit['total_rising']))
            print(("Falling edges: %i" % bit["total_falling"]))
            print(("Average freq: %s" % bit['avg_freq']))
            print(("Duty cycle: %s" % bit['duty_cycle']))
        print(("*" * 70))
        return active_bits

    def plot_all(self):
        """
        Plot all active bits.

        Yikes.  Come up with a better way to show this.

        """
        import matplotlib.pyplot as plt

        for bit in range(32):
            if len(self.get_events_by_bit(bit)) > 0:
                data = self.get_bit(bit)
                plt.plot(data)
        plt.show()

    def plot_bits(self, bits):
        """
        Plots a list of bits.
        """
        import matplotlib.pyplot as plt

        for bit in bits:
            data = self.get_bit(bit)
            plt.plot(data)
        plt.show()

    def close(self):
        """
        Closes the dataset.
        """
        self.dfile.close()


def main():
    path = r"\\aibsdata\mpe\CAM\testdata\test.h5"
    dset = Dataset(path)

    # pprint.pprint(dset.meta_data)

    dset.stats()

    # print dset.duty_cycle(2)

    # dset.plot_bits([2, 4])


if __name__ == '__main__':
    main()
