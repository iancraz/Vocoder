#!/usr/bin/env python3
"""Pass input directly to output.
https://app.assembla.com/spaces/portaudio/git/source/master/test/patest_wire.c
"""
import argparse

import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
import numpy as np

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = np.array(indata)*100

with sd.Stream(channels=1, callback=callback):
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()