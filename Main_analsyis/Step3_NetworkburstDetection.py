#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 22:05:53 2021

@author: xueerding
"""

import sys
import glob
import csv
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from itertools import chain
import math
import statistics as st

#inputFile = sys.argv[1]  # first field should be input file path
#inputFile = '/Users/xueerding/Desktop/MiCM/data/Extracted_files/Feb132020_ND3439SNCA_WTest3_2h/Feb132020_ND3439SNCA_WTest3_2h_well_list/D6_burst_list.csv'

def net_burst(inputFile):

    df = pd.read_csv(inputFile)
    
    sorted_data = df.sort_values('First spike time (sec)') #Sorts data from smallest electrode burst start time to largest 
    
    data = sorted_data.reset_index(drop = True) #Reset index in sorted data
    
    
    #Make IBeIH on log scale
    IBeI = data['First spike time (sec)'].diff()
    #IBeI.dropna(inplace=True)
    #print(IBeI)
    
    #Dictionary containng the y value for all bars in the histogram, the x values for all the bins, the value of all peaks after IBP, and the time of all peaks after IBP (as four separate lists)
    histdata_dict = {}
    
    (n, bins, patches) = plt.hist(IBeI, bins=np.logspace(np.log10(0.001),np.log10(10),num=50,endpoint=True, base=10,dtype=None),edgecolor='black')
    plt.gca().set_xscale("log")
    plt.title('logIBeIH histogram')
    plt.xlabel('IBeI log scale (sec)')
    plt.ylabel('Frequency')
    #plt.show()
    plt.savefig(inputFile[:-10] + 'log_IBeIH.png') 
    plt.close()
    
    histdata_dict['frequency'] = np.array(n)
    histdata_dict['bins'] = np.array(bins)
    
    #Extract x and y values of local maxima     
    x_valuelist =[] #List of the x values of all the peaks found in the histogram
    y_valuelist = [] #List of the y values of all the peaks found in the histogram
    maxima_array = argrelextrema(n, np.greater) #gives indices of local maxima in a numpy array
    maxima_lists= np.array(maxima_array).tolist() 
    maxima_list = list(map(int, chain.from_iterable(maxima_lists))) #turns the numpy array of indices into a flattened list
    for i in maxima_list:
        x_value = bins[i]
        y_value = n[i]
        x_valuelist.append(x_value)
        y_valuelist.append(y_value)
        
    #Identify the highest peak before 0.1 sec threshold and all peaks after it 
    pre_x = [] #the times of all the maxima before the 0.1 sec thresh
    pre_y = [] #the frequencies of all the maxima before the 0.1 sec thresh
    post_x = [] #all the maxima times after the 0.1 sec thresh
    post_y = [] #all the maxima frequencies after the 0.1 sec thresh
    
    histdata_dict['post_y'] = post_y
    histdata_dict['post_x'] = post_x
    
    for x,y in zip(range(len(x_valuelist)),range(len(y_valuelist))):
        if x_valuelist[x] <= 0.1:
            pre_x.append(x_valuelist[x])
            pre_y.append(y_valuelist[y])
        if x_valuelist[x] > 0.1:
            post_x.append(x_valuelist[x])
            post_y.append(y_valuelist[y])
            
    if len(pre_y) > 0 and len(post_y) > 0: #IF there are peaks present both before and after the threshold continue using the adaptive method
        minvalue_dict = {} #Dictionary contains all the minimum values between the IBP and subsequent peaks, their index, and the value of the subsequent peak being looked at (this information will be used to calculate the void paramater) 
    
        index_max = pre_y.index(max(pre_y))#The index of the highest peak
        peak_time = pre_x[index_max] #the time of the highest peak before the thresh
        peak_freq = pre_y[index_max] #the frequency of the highest peak before the thresh    
        histdata_dict['post_y'] += post_y
        histdata_dict['post_x'] += post_x
        
        #Identifying all the minimum values between the IBP and subsequent peaks after the threshold
        minvalues = [] #a list of all minima found between the IBP and subsequent peaks
        minindex = [] #the index of the all the minima 
        sub_peak = [] #the value of the subsequent peaks
        center_freq = [] #The y values of all the bars located between the IBP and subsequent peak being looked at
        center_times =[] #The x value of all the bars locacted between the IBP and subsequent peak being looked at 
        minvalue_dict['minvalues'] = minvalues
        minvalue_dict['minindex'] = minindex
        minvalue_dict['sub_peak'] = sub_peak
        minvalue_dict['center_freq'] = center_freq
        minvalue_dict['center_times'] = center_times
        
        #print(histdata_dict['post_x'])
        #print(histdata_dict['post_y'])
        for peakt, peakf in zip(histdata_dict['post_x'], histdata_dict['post_y']): #For the time and frequency of all subsequent peaks
            for freq, time in zip(histdata_dict['frequency'], histdata_dict['bins']): #For the frequency and time of all bins in the histograms
                if time > peak_time and time < peakt: #if the time of a bin is after the IBP and before the subsequent peak, add it to the centervalues
                    center_freq.append(freq)
                    center_times.append(time)          
            mincenter = center_freq.index(min(center_freq))
            minvalues.append(center_freq[mincenter])
            minindex.append(center_times[mincenter])
            sub_peak.append(peakf)
            center_freq = []
            center_times = []
    
        minvalue_dict['minvalues'] += minvalues
        minvalue_dict['minindex'] += minindex
        minvalue_dict['sub_peak'] += sub_peak
        
        #Calculate the void parameter between the IBP and each subsequent peak
        void_list = []
        minvalue_dict['void_list'] = void_list = []
        for minimum, peak in zip(minvalue_dict['minvalues'], minvalue_dict['sub_peak']):  # 0 is minvalues, 2 is sub_peak
            void = 1 - (minimum/math.sqrt(peak_freq*peak))
            void_list.append(void)
        minvalue_dict['void_list'] = void_list
        
        #Find the smallest minimum peak for which the void parameter is greater than 0.7        
        accepted_time = [] #A list of minima that have a void parameter above 0.7
    
        for void, minimum, time in zip(minvalue_dict['void_list'],minvalue_dict['minvalues'],minvalue_dict['minindex']):
            if void > 0.7:
                accepted_time.append(time)
        if len(accepted_time) > 0:
            IBeIth = min(accepted_time)
        elif len(accepted_time) == 0: #If there is no void parameter above 0.7 then use the fixed threshold method (fixed threshold of 100ms)
            IBeIth = 0.1
                
    if len(pre_y) == 0 or len(post_y) == 0: #If there is not altleast one peak before 100ms and one peak after 100ms then use the fixed threshold method (fixed threshold of 100ms)
        IBeIth = 0.1
        
    
    #Extracting burst information (note at what time each burst starts, the number of spikes ivolved, what time the last spike occurs at)            
    minpercent = 0.1875 #this is the threshold for the minimum number of spikes allowed in a burst
    num_bursting = 16 #the number of bursting electrodes 
    
    #extract raw electrode burst data into lists
    electrode_list = data['Electrode'].tolist()
    spike_list = data['Number of spikes'].tolist()
    first_list = data['First spike time (sec)'].tolist()
    last_list = data['Last spike time (sec)'].tolist()
    dur_list = data['Burst duration'].tolist()
    
    #Set up lists that will hold new network burst data, each list will be written into the respective excel columns created above
    burst_number = []
    num_electrode =[]
    burst_start = []
    burst_end = []
    netburst_dur = []
    elecburst_dur = []
    spike_number = []
    
    #lists that will be used to extract data out of the raw electrode burst data and into the above lists 
    network_start = []
    network_end = []
    electrode = []
    spike_num = []
    duration =[]
    
    csv_columns = ["Number of electrode bursts",
                   "Number of electrodes", 
                   "Beginning of network burst (s)", 
                   "End of network burst (s)", 
                   "Network burst duration (s)",
                   "Average electrode burst duration (s)",
                   "Number of spikes"]
    
    csv_name = inputFile[:-10] + 'networkBursts.csv'
    
    with open (csv_name, 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
    
        #extract parameters from raw electrode burst data
        for start, elec, end, spike, dur in zip(range(len(first_list)),range(len(electrode_list)),range(len(last_list)), range(len(spike_list)), range(len(dur_list))): 
            if first_list[start] - first_list[start-1] < IBeIth:#If the time between the start of two electrode bursts is below the IBeIth then count it as being part of an electrode burst
                if first_list[start] - first_list[start-1] > 0:
                    if first_list[start-1] not in network_start: #extracts start times of all electrode bursts in a NB
                        network_start.append(first_list[start-1])
                    network_start.append(first_list[start])
                    if last_list[end-1] not in network_end: #extracts end times of all EB in a NB
                        network_end.append(last_list[end-1])
                    network_end.append(last_list[end])
                    if spike_list[spike-1] not in spike_num: #extracts number of spikes in each EB present in a NB
                        spike_num.append(spike_list[spike-1])
                    spike_num.append(spike_list[spike])
                    if dur_list[dur-1] not in duration: #extracts the burst duration of each EB in a NB
                        duration.append(dur_list[dur-1])
                    duration.append(dur_list[dur])
                    if electrode_list[elec-1] not in electrode: #keeps track fo which electrode is bursting
                        electrode.append(electrode_list[elec-1])
                    electrode.append(electrode_list[elec])
                    
            else: 
                elec_number = set(electrode) #if the number of electrodes present is laregr than 20% of all bursting electrodes than we can classify the cluster of electrode bursts as a NB
                if len(network_start)>0 and len(elec_number) >= (minpercent*num_bursting) and sum(spike_num) >= 50:
                    burst_number.append(len(network_start))
                    burst_start.append(min(network_start))
                    burst_end.append(max(network_end))
                    elecburst_dur.append(st.mean(duration))
                    netburst_dur.append(max(network_end) - min(network_start))
                    spike_number.append(sum(spike_num))
                    num_electrode.append(len(elec_number))
                    
                    dict_data = {"Number of electrode bursts" : len(network_start),
                                 "Number of electrodes" : len(elec_number), 
                                 "Beginning of network burst (s)" : min(network_start), 
                                 "End of network burst (s)" : max(network_end), 
                                 "Network burst duration (s)" : max(network_end) - min(network_start),
                                 "Average electrode burst duration (s)" : st.mean(duration),
                                 "Number of spikes" : sum(spike_num)}
                    writer.writerow(dict_data)
                    
                    network_start = []
                    network_end = []
                    electrode = []
                    spike_num = []
                    duration =[]
                    
                else:
                    network_start = []
                    network_end = []
                    electrode = []
                    spike_num = []
                    duration =[]
                
    csvfile.close()
    
input_folder = sys.argv[1]  # first command line argument should be input directory  # first field should be input file path
#inputFile = '/Users/xueerding/Desktop/MiCM/data/Extracted_files/Feb132020_ND3439SNCA_WTest3_2h/Feb132020_ND3439SNCA_WTest3_2h_well_list/D6_spikes.csv'

# find spike files in input folder
files = glob.glob(input_folder + '/**/*_bursts.csv', recursive=True)

# calculate power spectrum for every spike file
for inputFile in files:
    net_burst(inputFile)
    