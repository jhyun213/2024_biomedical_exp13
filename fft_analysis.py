import wfdb
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import scipy.fftpack

dataset_dir = '../physionet.org/files/mitdb/1.0.0'

def plot_segment(sig, r_peaks, types, index, n_segments=5):
    r = r_peaks[index]
    window = n_segments//2
    idx_left = max(0, index-window)
    idx_right = min(index+window, len(r_peaks)-1)
    r_left = r_peaks[idx_left]
    r_right = r_peaks[idx_right]
    samples = np.arange(r_left, r_right)

    fig, axes=  plt.subplots(figsize=(10, 5))
    axes.plot(samples, sig[samples])
    for idx in range(idx_left, idx_right+1):
        axes.axvline(r_peaks[idx], c='r', ls=':')
        axes.annotate('{}th beat\ntype: {}'.format(idx, types[idx]), (r_peaks[idx], sig[r_peaks[idx]]))
    fig.savefig('plot.png')
    return samples, sig[samples]

def plot_fft(sig, fs, ylim=None):
    n = sig.shape[0]
    sig_f = scipy.fftpack.fft(sig)
    sig_f_roll = np.roll(sig_f, n//2)
    f = scipy.fftpack.fftfreq(n, 1/fs)
    f_roll = np.roll(f, n//2)

    fig, axes = plt.subplots(figsize=(10, 5))
    axes.plot(f_roll, np.abs(sig_f_roll))
    if ylim is not None:
        axes.set_ylim(bottom=ylim[0], top=ylim[1])
    fig.savefig('fft.png')

if __name__ == "__main__":
    patient = 106

    ## load record
    record_path = dataset_dir+'/'+str(patient)
    # record = wfdb.rdrecord(record_path, smooth_frames=False)
    record = wfdb.rdrecord(record_path)
    sig =record.p_signal[:, record.sig_name.index('MLII')]
    annotations = wfdb.rdann(record_path, 'atr')
    r_peaks = annotations.sample
    types = annotations.symbol

    _, x = plot_segment(sig, r_peaks, types, 10)
    plot_fft(x, 360, (0, 100))
