"""
Author: Sanna Wager
Created on: 9/18/19

This script provides an implementation of pitch shifting using the "time-domain pitch synchronous
overlap and add (TD-PSOLA)" algorithm. The original PSOLA algorithm was introduced in [1].

Description
The main script td_psola.py takes raw audio as input and applies steps similar to those described in [2].
First, it locates the time-domain peaks using auto-correlation. It then shifts windows centered at the
peaks closer or further apart in time to change the periodicity of the signal, which shifts the pitch
without affecting the formant. It applies linear cross-fading as introduced in [3] and implemented in
[4], the algorithm used for Audacity's simple pitch shifter.

Notes:
- Some parameters in the program related to frequency are hardcoded for singing voice. They can be
    adjusted for other usages.
- The program is designed to process sounds whose pitch does not vary too much, as this could result
    in glitches in peak detection (e.g., octave errors). Processing audio in short segment (e.g.,
    notes or words) is recommended. Another option would be to use a more robust peak detection
    algorithm, for example, pYIN [5]
- Small pitch shifts (e.g., up to 700 cents) should not produce many artifacts. Sound quality degrades
    if the shift is too large.
- The signal is expected to be voiced. Unexpected results may occur in the case of unvoiced signals

References:
Overlap and add algorithm exercise from UIUC
[1] F. Charpentier and M. Stella. "Diphone synthesis using an overlap-add technique for speech waveforms
    concatenation." In Int. Conf. Acoustics, Speech, and Signal Processing (ICASSP). Vol. 11. IEEE, 1986.
[2] https://courses.engr.illinois.edu/ece420/lab5/lab/#overlap-add-algorithm
[3] https://www.surina.net/article/time-and-pitch-scaling.html
[4] https://gitlab.com/soundtouch
[5] https://code.soundsoftware.ac.uk/projects/pyin
"""

import numpy as np
from numpy.fft import fft, ifft
import matplotlib.pyplot as plt
import librosa


def shift_pitch(signal, fs, f_ratio):
    """
    Calls psola pitch shifting algorithm
    :param signal: original signal in the time-domain
    :param fs: sample rate
    :param f_ratio: ratio by which the frequency will be shifted
    :return: pitch-shifted signal
    """
    peaks = find_peaks(signal, fs)
    new_signal = psola(signal, peaks, f_ratio)
    return new_signal


def find_peaks(signal, fs, max_hz=950, min_hz=75, analysis_win_ms=40, max_change=1.005, min_change=0.995):
    """
    Find sample indices of peaks in time-domain signal
    :param max_hz: maximum measured fundamental frequency
    :param min_hz: minimum measured fundamental frequency
    :param analysis_win_ms: window size used for autocorrelation analysis
    :param max_change: restrict periodicity to not increase by more than this ratio from the mean
    :param min_change: restrict periodicity to not decrease by more than this ratio from the mean
    :return: peak indices
    """
    N = len(signal)
    min_period = fs // max_hz
    max_period = fs // min_hz

    # compute pitch periodicity
    sequence = int(analysis_win_ms / 1000 * fs)  # analysis sequence length in samples
    periods = compute_periods_per_sequence(signal, sequence, min_period, max_period)

    # simple hack to avoid octave error: assume that the pitch should not vary much, restrict range
    mean_period = np.mean(periods)
    max_period = int(mean_period * 1.1)
    min_period = int(mean_period * 0.9)
    periods = compute_periods_per_sequence(signal, sequence, min_period, max_period)

    # find the peaks
    peaks = [np.argmax(signal[:int(periods[0]*1.1)])]
    while True:
        prev = peaks[-1]
        idx = prev // sequence  # current autocorrelation analysis window
        if prev + int(periods[idx] * max_change) >= N:
            break
        # find maximum near expected location
        peaks.append(prev + int(periods[idx] * min_change) +
                np.argmax(signal[prev + int(periods[idx] * min_change): prev + int(periods[idx] * max_change)]))
    return np.array(peaks)


def compute_periods_per_sequence(signal, sequence, min_period, max_period):
    """
    Computes periodicity of a time-domain signal using autocorrelation
    :param sequence: analysis window length in samples. Computes one periodicity value per window
    :param min_period: smallest allowed periodicity
    :param max_period: largest allowed periodicity
    :return: list of measured periods in windows across the signal
    """
    offset = 0  # current sample offset
    periods = []  # period length of each analysis sequence

    while offset < N:
        fourier = fft(signal[offset: offset + sequence])
        fourier[0] = 0  # remove DC component
        autoc = ifft(fourier * np.conj(fourier)).real
        autoc_peak = min_period + np.argmax(autoc[min_period: max_period])
        periods.append(autoc_peak)
        offset += sequence
    return periods


def psola(signal, peaks, f_ratio):
    """
    Time-Domain Pitch Synchronous Overlap and Add
    :param signal: original time-domain signal
    :param peaks: time-domain signal peak indices
    :param f_ratio: pitch shift ratio
    :return: pitch-shifted signal
    """
    N = len(signal)
    # Interpolate
    new_signal = np.zeros(N)
    new_peaks_ref = np.linspace(0, len(peaks) - 1, len(peaks) * f_ratio)
    new_peaks = np.zeros(len(new_peaks_ref)).astype(int)

    for i in range(len(new_peaks)):
        weight = new_peaks_ref[i] % 1
        left = np.floor(new_peaks_ref[i]).astype(int)
        right = np.ceil(new_peaks_ref[i]).astype(int)
        new_peaks[i] = int(peaks[left] * (1 - weight) + peaks[right] * weight)

    # PSOLA
    for j in range(len(new_peaks)):
        # find the corresponding old peak index
        i = np.argmin(np.abs(peaks - new_peaks[j]))
        # get the distances to adjacent peaks
        P1 = [new_peaks[j] if j == 0 else new_peaks[j] - new_peaks[j-1],
              N - 1 - new_peaks[j] if j == len(new_peaks) - 1 else new_peaks[j+1] - new_peaks[j]]
        # edge case truncation
        if peaks[i] - P1[0] < 0:
            P1[0] = peaks[i]
        if peaks[i] + P1[1] > N - 1:
            P1[1] = N - 1 - peaks[i]
        # linear OLA window
        window = list(np.linspace(0, 1, P1[0] + 1)[1:]) + list(np.linspace(1, 0, P1[1] + 1)[1:])
        # center window from original signal at the new peak
        new_signal[new_peaks[j] - P1[0]: new_peaks[j] + P1[1]] += window * signal[peaks[i] - P1[0]: peaks[i] + P1[1]]
    return new_signal


if __name__=="__main__":
    # Load audio
    orig_signal, fs = librosa.load("female_scale.wav", sr=44100)
    N = len(orig_signal)

    # Pitch shift amount as a ratio
    f_ratio = 2 ** (-2 / 12)

    # Shift pitch
    new_signal = shift_pitch(orig_signal, fs, f_ratio)

    # Plot
    plt.style.use('ggplot')
    plt.plot(orig_signal[:-1])
    plt.show()
    plt.plot(new_signal[:-1])
    plt.show()

    # Write to disk
    librosa.output.write_wav("female_scale_transposed_{:01.2f}.wav".format(f_ratio), new_signal, fs)
