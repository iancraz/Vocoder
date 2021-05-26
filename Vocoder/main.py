import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    CHUNK = 1024*4
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    p = pyaudio.PyAudio()
    # stream = p.open(format=FORMAT,
    # channels=CHANNELS,
    # rate=RATE,
    # input=True,
    # output=True,
    # frames_per_buffer=CHUNK)

    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))

#     frames = []

#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         print(f"recording {i}", end='\r')
#         data = stream.read(CHUNK)
#         # print(data)
#         # data_int = np.array(struct.unpack(str(2*CHUNK)+'B', data), dtype='b')[::2] + 127
#         data = np.fromstring(data, 'int16');
#         frames.append(data)

#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#     frames = np.array(frames)
#     print(frames.shape)

#     plt.plot(frames.flatten())
#     plt.show()


# # stream.write(signal.tobytes())
# # https://stackoverflow.com/questions/64801274/sound-played-with-pyaudio-seems-correct-but-too-short