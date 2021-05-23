import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
duration = 5.5  # seconds

data = []
def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata
    data.append(outdata)

with sd.Stream(channels=2, callback=callback):
    sd.sleep(int(duration * 1000))

data = np.array(data)
print(data.shape)
print(data.flatten())
plt.plot(data[:,0].flatten())
plt.show()