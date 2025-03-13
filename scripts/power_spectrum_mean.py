#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 08:29:27 2021

@author: xueerding
"""

import sys
import glob
import os
import numpy as np
import pandas as pd

import math
from scipy import signal
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20, 10)

powspec = {}  # initialize dict of power spectrums
bin_size = 0.0005  # default bin size
input_folder = sys.argv[1]  # first command line argument should be input directory

# check if custom bin size set
if len(sys.argv) == 3:
    try:
        if float(sys.argv[2]) > 0:
            bin_size = float(sys.argv[2])
        else:
            print('bin size must be positive')
    except:
        print('bin size not valid')


# find spike files in input folder
files = glob.glob(input_folder + '/**/*spikes.csv', recursive=True)

# calculate power spectrum for every spike file
for inputFile in files:

    df = pd.read_csv(inputFile, usecols=["Electrode", "Time (s)"])
    
    spike_list = df['Time (s)'].to_numpy()
    
    
    # set bin size (s)
    n_bins = np.ceil(np.max(spike_list) / bin_size).astype(int)
    '''
    bins = np.arange(0, math.ceil(df["Time (s)"].max()), bin_size)
    timeSeries = pd.Series(data=np.zeros(bins.size, dtype='int'))
    
    # get spike count per time bin
    bin_num = 0
    for spike in spike_list:
        while spike > bins[bin_num]:
            bin_num += 1
            if bin_num == bins.size:
                bin_num -= 1
                break
        timeSeries.at[bin_num] += 1
    '''
    spike_count, bin_interval = np.histogram(spike_list,n_bins)
    
    # calculate power spectral density using Welch's method
    freq, psd = signal.welch(spike_count, fs=1/bin_size, scaling='spectrum')
    powspec[inputFile[-16:-11]] = psd
    plt.plot(freq, psd, '--')

# average the power spectral densities
powspec_df = pd.DataFrame(data=powspec)
powspec_df['mean'] = powspec_df.mean(axis=1)
print(powspec_df)

# plot average power spectral density
plt.plot(freq, powspec_df['mean'], linewidth=2.5)
plt.title(input_folder + ' average power spectral density with ' + str(1/bin_size) + ' Hz sampling frequency')
plt.xlabel('frequency [Hz]')
plt.ylabel('PS [V**2/Hz]')
plt.legend(powspec.keys())
plt.tight_layout()
#plt.show()
plt.savefig(input_folder + '/mean_pow_spec_freq_' + str(int(1/bin_size)) + '.png')

