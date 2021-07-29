import fire
import numpy as np
import re
import json
from scipy import signal
from pathlib import Path

def get_file(file):
    return np.genfromtxt(file)
def get_resp(phys_path, json_path, max_length):
    with open(json_path) as f:
        j = json.load(f)
    resp = np.genfromtxt(phys_path)[:, j["Columns"].index("respiratory")][:max_length]
    return resp
def downsample_resp(resp, length):
    resp_resampled = signal.resample(resp, length)
    return resp_resampled

def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a
def extract_max_freq(resp_trace, sampling_rate):
    fourier_transform = np.fft.rfft(resp_trace)
    abs_fourier_transform = np.abs(fourier_transform)
    power_spectrum = np.square(abs_fourier_transform)
    frequency = np.linspace(0, sampling_rate/2, len(power_spectrum))
    assert len(power_spectrum) == len(frequency)
    return frequency[np.argmax(power_spectrum)]


def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def filter_frequency(data):
    return butter_bandpass_filter(data, 0.05, 1, 62.5)


def run(hires_motionfile, phys_path, json_path, maxlength, resp_freq):
    filtered = get_file(hires_motionfile)
    resp = get_resp(phys_path, json_path, maxlength)
    max_freq = extract_max_freq(resp - resp.mean(), resp_freq); print(max_freq)
    filtered_freq = filter_frequency(resp)
    print(filtered_freq.shape)
    resp_resampled = downsample_resp(filtered_freq, len(filtered))
    print(resp_resampled.shape)
    print(filtered.shape)
    print(np.corrcoef(resp_resampled, filtered))

fire.Fire(run)
