#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 10:09:39 2021

@author: xueerding
"""

import sys
import glob
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def burst(inputFile):
    df = pd.read_csv(inputFile, usecols=["Electrode", "Time (s)"], 
                 dtype={"Electrode":'str', "Time (s)":'float'})
    
    df.dropna(inplace=True)
    
    temp = df.groupby(["Electrode"]).agg(list)
    
    data = temp.filter(regex="._.", axis=0)
    
    data_dict = data.to_dict(orient='index')
    
    data2 = pd.DataFrame( {key:pd.Series(value['Time (s)']) for key, value in data_dict.items()} )
    spike_data = data2.astype('float64')
    
    # plot logISI histogram
    ISIs = spike_data.diff()
    ISI_list = []
    for elec in ISIs.columns:
        ISI_list += ISIs[elec].dropna().tolist()
        
    (n, bins, patches) = plt.hist(ISI_list, bins=np.logspace(np.log10(0.001),np.log10(10),num=50,endpoint=True, base=10,dtype=None),edgecolor='black')
    plt.gca().set_xscale("log")
    plt.title('logISI histogram')
    plt.xlabel('ISI log scale (sec)')
    plt.ylabel('Frequency')
    #plt.show()
    plt.savefig(inputFile[:-10] + 'log_ISI.png') 
    plt.close()
    
    # detect bursts using ISI threshold method
    minspikes = 5  # threshold for the minimum number of spikes allowed in a burst
    maxISI = 0.1  # maximum inter spike interval allowed in a burst
    
    burst_dict = {}
    
    csv_columns = ["Electrode",
                   "Number of spikes", 
                   "First spike time (sec)", 
                   "Last spike time (sec)", 
                   "Burst duration"]
    csv_name = inputFile[:-10] + 'bursts.csv'
    
    with open (csv_name, 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        
        for elec in spike_data:
            burst_number = []
            burst_start = []
            burst_end = []
            burst_duration = []
            
            start = 0
            end = 1
            spike_num = 1
        
            spike_array = spike_data[elec].array
            #print(spike_array)
            
            while end < len(spike_array) and ~np.isnan(spike_array[end]):
                ISI = spike_array[end] - spike_array[end-1]
                if ISI <= maxISI:
                    spike_num += 1
                    end += 1
                else:
                    if spike_num >= minspikes:
                        burst_number.append(spike_num)
                        burst_start.append(spike_array[start])
                        burst_end.append(spike_array[end-1])
                        burst_duration.append(spike_array[end-1] - spike_array[start])
                        
                        dict_data = {"Electrode" : elec,
                                     "Number of spikes" : spike_num, 
                                     "First spike time (sec)" : spike_array[start], 
                                     "Last spike time (sec)" : spike_array[end-1], 
                                     "Burst duration" : spike_array[end-1] - spike_array[start]
                                     }
                        writer.writerow(dict_data)
                        
                        spike_num = 1
                        start = end
                        end = start + 1
                    else:
                        spike_num = 1
                        start = end
                        end = start + 1
                    
            burst_dict[elec] = {"Number of spikes" : burst_number,
                                "First spike time (sec)" : burst_start,
                                "Last spike time (sec)" : burst_end,
                                "Burst duration" : burst_duration }
    csvfile.close()


input_folder = sys.argv[1]  # first command line argument should be input directory  # first field should be input file path
#inputFile = '/Users/xueerding/Desktop/MiCM/data/Extracted_files/Feb132020_ND3439SNCA_WTest3_2h/Feb132020_ND3439SNCA_WTest3_2h_well_list/D6_spikes.csv'

# find spike files in input folder
files = glob.glob(input_folder + '/**/*spikes.csv', recursive=True)

# calculate power spectrum for every spike file
for inputFile in files:
    burst(inputFile)
    

    
    
    
    
        
        
    