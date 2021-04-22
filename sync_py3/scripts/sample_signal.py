"""
Just flips two Digital IO lines at different rates.

This should be expanded to generate different types of signals and perhaps be
    part of a testing suite.

"""
from toolbox.IO.nidaq import DigitalOutput
import numpy as np
import time

do = DigitalOutput("Dev2", port=1)
do.start()


counter = 0
counter_2 = 0
print("Running...")
while True:
    to_write = counter % 2
    do.writeBit(0, to_write)
    if counter % 2 == 0:
        to_write = counter_2 % 2
        do.writeBit(1, to_write)
        counter_2 += 1
    counter += 1
    if counter % 1000 == 0:
        print(counter)
    # time.sleep(0.1)

do.stop()
do.clear()
