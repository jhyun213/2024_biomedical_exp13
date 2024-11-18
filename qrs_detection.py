import argparse
import time
import wfdb
from wfdb import processing
from wfdb.processing.basic import resample_singlechan
import numpy as np
import matplotlib.pyplot as plt
from sys import getsizeof

PATIENTS = [101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215, 220, 223, 230, 100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231, 232, 233, 234]

dataset_dir = '../physionet.org/files/mitdb/1.0.0'

def check_args(args):
    patient = args.patient
    if not patient in PATIENTS:
        raise ValueError('invalid patient')

def qrs_detection(args):
    patient = args.patient
    fs = args.fs

    ## load record and annotation
    record_path = dataset_dir+'/'+str(patient)
    # record = wfdb.rdrecord(record_path, smooth_frames=False)
    record = wfdb.rdrecord(record_path)

    sig =record.p_signal[:, record.sig_name.index('MLII')]
    annotations = wfdb.rdann(record_path, 'atr')

    ## quantization
    print(sig.dtype)
    sig = sig.astype(np.float16)

    ## resampling
    sig_resamp, ann_resamp = resample_singlechan(sig, annotations, 360, fs)
    # sig_resamp, ann_resamp = sig, annotations
    r_peaks = ann_resamp.sample
    types = ann_resamp.symbol
    print('original signal size: ', sig.nbytes)
    print('resampled signal size: ', sig_resamp.nbytes)

    ## QRS detector
    xqrs = processing.XQRS(sig=sig_resamp, fs=fs)
    start_time = time.time()
    xqrs.detect()
    finish_time = time.time()
    comparitor = processing.Comparitor(r_peaks[1:], xqrs.qrs_inds, int(fs*0.1), sig_resamp)
    comparitor.compare()
    print('QRS detection runtime: ', (finish_time-start_time))
    comparitor.print_summary()
    comparitor.plot(figsize=(15, 8))
    plt.savefig('qrs_results.png'.format(patient, fs))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--patient',
        help='patient number',
        required=True,
        type=int
    )
    parser.add_argument(
        '-fs',
        help='sampling frequency',
        required=True,
        type=int
    )
    args = parser.parse_args()
    check_args(args)
    qrs_detection(args)
