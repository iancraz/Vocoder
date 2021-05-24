import pyaudio
import msvcrt
import Vocoder as gp
import numpy as np
import matplotlib.pyplot as plt
import Vocoder as vc
from scipy.io.wavfile import write

# Definition of chords

frecuencies = [500,500,500]
chords = {'A': [110,138.5913,164.8138] , 'B':[123.4708,155.5635,184.9972], 'C':[130.8128,164.8138,195.9977],
                   'D':[146.8324,184.9972,220.0000], 'E':[164.8138,207.6523,246.9417], 'F':[174.6141,220.0000,261.6256],
                    'G':[195.9977,246.9417,293.6648], 'Am':[110,130.8128,164.8138], 'Bm':[123.4708,146.8324,184.9972],
                    'Cm':[130.8128,155.5635,195.9977], 'Dm':[146.8324,174.6141,220.0000], 'Em':[164.8138,195.9977,246.9417],
                    'Fm':[174.6141,207.6523,261.6256], 'Gm':[195.9977,233.0819,293.6648]}
keyboard2chords = {'a':chords['A'], 's':chords['B'], 'd':chords['C'], 'f':chords['D'], 'g':chords['E'], 'h':chords['F'],
                   'j':chords['G'], 'z':chords['Am'], 'x':chords['Bm'], 'c':chords['Cm'], 'v':chords['Dm'], 'b':chords['Em'],
                   'n':chords['Fm'], 'm':chords['Gm']}

#PyAudio Stuff

CHUNK = 2**13
WIDTH = 2
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 999999
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

#Start processing
overlp = 0.5
block_secs = 0.04
fs = RATE
glob_arr = np.zeros(CHUNK)
prev_half_block_sintetized = np.zeros(int(overlp*block_secs*fs))


WAV_TEST = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):

    if msvcrt.kbhit():
        frecuencies = keyboard2chords[msvcrt.getwch()]
        print(f"Las frecuencias utilizadas son: {frecuencies[0]},{frecuencies[1]},{frecuencies[2]}")
    data = stream.read(CHUNK)
    input = np.fromstring(data,'int16')
    input = input/(2**15)


    out1 = vc.vocode(input, fs, f_custom=frecuencies[0], block_len=block_secs, overlap=overlp, order=16, prev_block=prev_half_block_sintetized)
    out2 = vc.vocode(input, fs, f_custom=frecuencies[1], block_len=block_secs, overlap=overlp, order=16, prev_block=prev_half_block_sintetized)
    out3 = vc.vocode(input, fs, f_custom=frecuencies[2], block_len=block_secs, overlap=overlp, order=16, prev_block=prev_half_block_sintetized)
    out = (out1 + out2 + out3)/3
    out = out * 2**15
    out = out.astype(np.int16)
    asd = out.tobytes()
    stream.write(asd, CHUNK)
    # prev_half_block_sintetized = out[len(out)-len(prev_half_block_sintetized):]


WAV_TEST = np.array(WAV_TEST).flatten()
WAV_TEST = (WAV_TEST + 1)/2 *255

write("example.wav", RATE,WAV_TEST)


#PyAudio Terminators

stream.stop_stream()
stream.close()
p.terminate()