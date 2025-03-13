#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 10:26:39 2021

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

def pow_spec(inputFile, bin_size):
    # this function computes and plots the power spectral density using Welch's method with the desired sampling frequency
    # read csv into dataframe
    df = pd.read_csv(inputFile, usecols=["Electrode", "Time (s)"], 
                     dtype={"Electrode":'str', "Time (s)":'float'})
    
    spike_list = df['Time (s)'].to_numpy()
    
    # get spike count per time bin
    n_bins = np.ceil(np.max(spike_list) / bin_size).astype(int)
    spike_count, bin_interval = np.histogram(spike_list,n_bins)
    
    # plot power spectral density using Welch's method
    freq, psd = signal.welch(spike_count, fs=1/bin_size, scaling='density')
    
    plt.figure()
    plt.plot(freq, psd)
    plt.title(inputFile[:-4] +' power spectral density by well with ' + str(1/bin_size) + ' Hz sampling frequency\n')
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PS [V**2/Hz]')
    #plt.show()
    plt.savefig(inputFile[:-4] + '_pow_spec_freq_' + str(int(1/bin_size)) + '.png')
    plt.close()
    
    
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
    pow_spec(inputFile, bin_size)