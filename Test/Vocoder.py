import numpy as np
from scipy.signal import hann, lfilter, butter
from numpy import array, double, amax, absolute, zeros, floor, arange, mean
from numpy import correlate, dot, append, divide, argmax, int16, sqrt, power
from numpy.random import randn
from scipy.linalg import solve_toeplitz
import matplotlib.pyplot as plt
from scipy import signal

# Glottal Pulses Definition

def glotal_triangular(len_block, p_coverage=0.1, r1_start=0, r1_stop=3, r2_start=1, r2_stop=0):
  vocoded = np.zeros(len_block)
  ramp_len=int(len_block*p_coverage)//2
  ramp_up = np.linspace(r1_start, r1_stop,ramp_len,endpoint=False)
  ramp_down = np.linspace(r2_start,r2_stop,ramp_len*2)
  ramp = np.hstack((ramp_up, ramp_down))
  vocoded[len(vocoded)//2-ramp_len:len(vocoded)//2+ramp_len*2] = ramp
  return vocoded

def glotal_hamming(len_block, p_coverage=0.1):
  vocoded = np.zeros(len_block)
  len_hamming = int(len_block*p_coverage)
  if len_hamming%2 != 0:
    len_hamming = len_hamming + 1
  vocoded[len(vocoded)//2-len_hamming//2:len(vocoded)//2 + len_hamming//2] = np.hamming(len_hamming)
  return vocoded

def glotal_square(len_block, p_coverage=0.1):
  vocoded = np.zeros(len_block)
  square_len=int(len_block*p_coverage)//2
  vocoded[len(vocoded)//2-square_len:len(vocoded)//2+square_len] = 1
  return vocoded

def glotal_exp_rising(len_block, p_coverage=0.1, th= 0.1, amplitude= 1.0):
  vocoded = np.zeros(len_block)
  alpha = (-2/(p_coverage*len_block)) * np.log(th/amplitude)
  t = np.arange(-len_block//2, len_block//2)
  vocoded = amplitude * np.exp(-alpha * np.abs(t))
  return vocoded

# Pitch Maker Definition

def pitch_maker(len_block, T_samples, prev_delta, overlap=0.5):
  block = np.zeros(len_block)
  current_pos = int(len_block*overlap) + prev_delta
  if current_pos >= len_block:
    return block, prev_delta-len_block
  block[current_pos] = 1
  new_delta = 0
  finish = False
  temp_pos = current_pos
  while temp_pos >= 0:
    temp_pos = temp_pos - T_samples
    if temp_pos >= 0:
      block[temp_pos] = 1
  while not finish:
    dist = len_block-current_pos
    new_delta = T_samples-dist
    if new_delta < 0:
      current_pos = current_pos+T_samples
      block[current_pos] = 1
    else:
      finish = True
  return block, new_delta


# Vocoder

glotales = {"square": glotal_square, "triang": glotal_triangular, "exp": glotal_exp_rising, "hamming": glotal_hamming}

def block_process(data, fs, block_len, overlap):
  """
  A generator that slices an input array into overlapping blocks.
  data      the input array as a one dimensional numpy array.
  fs        the sample rate as integer number.
  block_len the length of one block in seconds.
  overlap   the percentage of overlap between blocks.
  """
  block_samples = round(block_len * fs)
  overlap_samples = round(block_samples * overlap)
  shift_samples = block_samples - overlap_samples
  num_blocks = int(floor((len(data) - overlap_samples) / shift_samples))
  for idx in range(0, num_blocks):
    samples = data[idx * shift_samples:idx * shift_samples + block_samples]
    yield (array(samples, copy=True), idx * shift_samples)

def fundamental_period_estimate(rxx, fs):
  """
  Calculates the fundamental frequency of an auto correlation array.
  rxx   the auto correlation array.
  fs    the sample rate in hertz.
  """
  f_low, f_high = 50, 250
  f_low_idx = round(fs / f_low)
  f_high_idx = round(fs / f_high)
  period_idx = argmax(rxx[f_high_idx:f_low_idx]) + f_high_idx
  is_voiced = max(rxx) > 0.20
  return (period_idx, is_voiced)

def vocode(signal, fs, f_custom, block_len, overlap, order, prev_block, p_coverage=0.01, unvoiced2zeros=True, glotal_type="triang"):
  """
  Analyzes a speech signal and synthesizes a vocoded speech signal.
  The speech signal is analyzed using the levinson-durben algorithm
  of the given order. Then, an corresponding output signal is
  synthesized from the levinson-durben coefficients.
  signal     the speech signal as a one dimensional numpy array.
  fs         the sample rate in hertz.
  block_len  the block processing block length in seconds.
  overlap    the block processing block overlap in percent (0..1).
  order      the number of coefficients to use.
  returns a vocoded signal of the same sample rate as the original.
  """

  b_butter, a_butter = butter(1, 200 / fs, 'high')
  glottal_lowpass = lambda signal, b, a: lfilter(b, a, signal)

  out = zeros(len(signal))
  out[:len(prev_block)] = prev_block
  # pitch tunning, ignore period samples
  prev_delta = 0
  T_samples = int((fs / f_custom))  # (muestras/segundo) / (1/segundo)

  for block, idx in block_process(signal, fs, block_len, overlap):
    gain_correction = (1 - overlap) * 2  # *2 due to hann window
    block *= hann(len(block)) * gain_correction

    rxx = correlate(block, block, mode='full')
    rxx = rxx[len(rxx) // 2:]
    period_samples, is_voiced = fundamental_period_estimate(rxx, fs)
    # LPC coefficients
    #block = preemphasis(block)
    #rxx = correlate(block, block, mode='full')
    #rxx = rxx[len(rxx) // 2:]
    a = -solve_toeplitz(rxx[:order], rxx[1:order + 1])
    a = np.concatenate(([1], a))
    error_power = rms(lfilter(a, (1,), block))
    if is_voiced:
      try:
        vocoded, new_delta = pitch_maker(len(block), T_samples, prev_delta, overlap=overlap)
        prev_delta = new_delta
        impulse_response = glotales[glotal_type](len(block), p_coverage=p_coverage)
        vocoded = np.convolve(vocoded, impulse_response, mode="same")
      except:
        continue
    else:
      if unvoiced2zeros:
        vocoded = np.zeros(len(block))  # randn(len(block))/2
      else:
        vocoded = randn(len(block)) / 2

    vocoded = lfilter((error_power,), a, vocoded)
    vocoded *= hann(len(block))
    out[idx:idx + len(block)] += preemphasis(vocoded)  # deemphasis(vocoded)
  return out

def preemphasis(signal):
  return lfilter([1, -0.70], 1, signal)

def deemphasis(signal):
  return lfilter([1, 0.70], 1, signal)

def rms(signal):
  return sqrt(mean(power(signal, 2)))

