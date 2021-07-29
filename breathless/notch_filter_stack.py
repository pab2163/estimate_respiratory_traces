import numpy as np
from scipy import signal
import os
import fire


def filter_notch(data, filt_val, freq, quality=5):
    b, a = signal.iirnotch(filt_val, quality, freq)
    y = signal.filtfilt(b, a, x=data, axis=0)
    b, a = signal.iirnotch(filt_val*2, quality, freq)
    y = signal.filtfilt(b, a, x=y, axis=0)
    b, a = signal.iirnotch(filt_val*3, quality, freq)
    y = signal.filtfilt(b, a, x=y, axis=0)
    return y

def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def run_filter(file, filt_val, freq):
    stack = np.genfromtxt(file)
    filtered_notch = filter_notch(stack, filt_val, freq)
    buttered = butter_bandpass_filter(filtered_notch[:, -1], 0.15, 0.6, freq)
    name = file.split(os.path.sep)[-1].split(".")[0]
    np.savetxt("{}_filtered.1D".format(name), buttered, fmt="%0.06f")
    return "{}_filtered.1D".format(name)


if __name__ == "__main__":
    fire.Fire(run_filter)
