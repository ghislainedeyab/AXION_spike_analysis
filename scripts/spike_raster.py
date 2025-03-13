#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 23:11:50 2021

@author: xueerding
"""

import sys
import glob
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import random as r 
from matplotlib.patches import Rectangle


def raster(inputFile):
    # this function plots the raster plot of the spike train for each electrode and the spike count histogram with 1 sec bins
    # read data into dataframe
    df = pd.read_csv(inputFile, usecols=["Electrode", "Time (s)"])
    
    df.dropna(inplace=True)
    
    temp = df.groupby(["Electrode"]).agg(list)
    
    data = temp.filter(regex="._.", axis=0)
    
    data_dict = data.to_dict(orient='index')
    
    data2 = pd.DataFrame( {key:pd.Series(value['Time (s)']) for key, value in data_dict.items()} )
    spike_df = data2.astype('float64')
    
    
    #Plot figure
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(20, 6))
    #fig.dpi=80
    fig.facecolor='w'
    fig.edgecolor='k'
    
    # plot spike histogram with 1 sec bins
    bin_size = 1
    spike_list = df['Time (s)'].to_numpy()
    '''
    bins = np.arange(0, math.ceil(df["Time (s)"].max()), bin_size)
    timeSeries = pd.Series(data=np.zeros(bins.size, dtype='int'))

    bin_num = 0
    for spike in spike_list:
        while spike > bins[bin_num]:
            bin_num += 1
            if bin_num == bins.size:
                bin_num -= 1
                break
        timeSeries.at[bin_num] += 1
    ax1.plot(bins, timeSeries)
    '''
    # get spike count per time bin
    n_bins = np.ceil(np.max(spike_list) / bin_size).astype(int)
    spike_count, bin_interval = np.histogram(spike_list,n_bins)
    
    ax1.plot(bin_interval[1:], spike_count)
    
    # plot raster plot
    for key, val in spike_df.items():
        if len(val) > 0:
            ax2.scatter(spike_df[key],[key]*len(val), marker="|", color = 'k', label=key)
            
        if len(val) == 0:
            rand = r.randint(70,90)
            ax2.scatter(rand,key,marker="|",color='w')
            
    # empty plot for electrodes with no spikes
    well = inputFile[-13:-11]
    print(well)
    electrode_list = []
    for i in range(1, 5):
        for j in range (1, 5):
            electrode_list.append(well + '_' + str(i) + str(j))
    
    for electrode in electrode_list:
        if electrode not in spike_df.columns:
            rand = r.randint(70,90)
            ax2.scatter(rand,electrode,marker="|",color='w', label=electrode)

    # check if burst info exists
    try:
        burstFile = inputFile[:-11] + '_bursts.csv'
        burst_df = pd.read_csv(burstFile)
        
        # dict of spike times involved in a burst by electrode
        elec_burst = {k: [] for k in spike_df.columns} 
        for index, row in burst_df.iterrows():
            for spike in spike_df[row['Electrode']]:
                if spike >= row['First spike time (sec)'] and  spike <= row['Last spike time (sec)']:
                    elec_burst[row['Electrode']].append(spike)
                    
        # plot burst info in raster plot    
        for key, val in elec_burst.items():
            ax2.scatter(elec_burst[key],[key]*len(val), marker="|", color = 'b', label=key)
    
    except IOError:
        print(burstFile + ' does not exist')
        
    # check if network burst info exists 
    try: 
        # plot network burst info in raster plot
        netBurstFile = inputFile[:-11] + '_networkBursts.csv'
        burst_df = pd.read_csv(netBurstFile)
        beg_NB = burst_df['Beginning of network burst (s)']
        end_NB = burst_df['End of network burst (s)']
        
        # (x,y) are the coordinates of the bottom left corner, width is in units of the x axis, and height is in units of y axis
        for beg, end in zip(beg_NB,end_NB):
            ax2.add_patch(Rectangle((beg, -0.5),(end-beg), 16, edgecolor = 'black',lw = 0.5, fill = False))
    
    except IOError:
        print(netBurstFile + ' file does not exist')
        
    plt.suptitle(inputFile)
    plt.xlabel('Time (sec)')
    plt.xlim(0,600)
    ax1.set_yscale('log', base=10, subs=[2,3,4,5,6,7,8,9])
    ax1.set_ylim(0.5, 10000)
    ax1.set_ylabel('Number of spikes/1 sec interval')
    ax2.set_ylabel('Electrode')
    plt.savefig(inputFile[:-4] + '_raster.png')
    #plt.show()
    plt.close()
   

input_folder = sys.argv[1]  # first command line argument should be input directory
        
# find spike files in input folder
files = glob.glob(input_folder + '/**/*spikes.csv', recursive=True)
# calculate power spectrum for every spike file
for inputFile in files:
    raster(inputFile)
