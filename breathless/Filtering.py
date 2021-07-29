import scipy.signal as signal


class Filtering:
    """ A class to run filtering operations"""

    def run_notch(self, data, filt_val, freq, quality):
        b, a = signal.iirnotch(filt_val, quality, freq)
        return signal.filtfilt(b, a, x=data, axis=0)

    def notch_harmonics(self, data, filt_val, freq, quality=5):
        out = self.run_notch(data, filt_val, freq, quality)  # Filter on the first val
        out = self.run_notch(
            out, filt_val * 2, freq, quality
        )  # Must also filter on harmonics
        out = self.run_notch(out, filt_val * 3, freq, quality)
        return out

    def butter_bandpass(self, data, lowcut, highcut, fs, order=3):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype="band")
        y = signal.filtfilt(b, a, data)
        return y
