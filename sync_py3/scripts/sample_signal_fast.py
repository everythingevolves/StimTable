"""
Sample signal.  High speed pulse output for benchmarking.
"""
import time

from toolbox.IO.nidaq import CounterOutputFreq


def main():
    co = CounterOutputFreq(
        'Dev2', 'ctr3', init_delay=0.0, freq=1000.0, duty_cycle=0.50
    )
    co.start()
    time.sleep(10)
    co.clear()


if __name__ == '__main__':
    main()
