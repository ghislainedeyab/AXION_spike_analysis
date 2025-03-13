#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import glob
import os
import csv
import pandas as pd

# extract parameters

def time(inputFile):
    """
    Parameters
    ----------
    inputFile : str
        path to input spike file

    Returns
    -------
    num : int
        number of spikes in file

    """
    with open(inputFile, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for row in csv_reader:
            if row[0] == "   Actual File Section Run":
                times = row[1].split(" to ")
                
                s = times[0].strip("s").split("m")
                start = 0
                if (len(s) == 2):
                    start = int(s[0])*60 + int(s[1])
                else:
                    start = int(s[0])
                    
                e = times[1].strip("s").split("m")
                end = 0
                if (len(e) == 2):
                    end = int(e[0])*60 + int(e[1])
                else:
                    end = int(e[0])
                
                break
            
        return int(end) - int(start)
    

def extract_parameters(inputFolder, time):
    """
    Parameters
    ----------
    inputFolder : str
        Path to input folder with spike files per well
    time : int
        recording time

    Returns
    -------
    well_list : dict
        Dictionary with extracted parameters per well

    """
    well_list = {}  # dict of extracted parameters per well
    
    # SPIKE INFO
    well_files = glob.glob(input_folder + '/**/*spikes.csv', recursive=True)
    for w_file in well_files:
        well = w_file[-13:-11]
        with open(w_file) as file:
            # count number of spikes for every well
            num_spikes = sum(1 for line in file)-1
            well_list[well] = {"Well": well, "Total spikes":num_spikes}

        # MFR
        # read input and aggregate by well
        df = pd.read_csv(w_file, usecols=["Electrode", "Time (s)"], 
                 dtype={"Electrode":'str', "Time (s)":'float'})
        df.dropna(inplace=True)
        temp = df.groupby(["Electrode"]).agg(list)
        data = temp.filter(regex="._.", axis=0)
        data_dict = data.to_dict(orient='index')
        data2 = pd.DataFrame( {key:pd.Series(value['Time (s)']) for key, value in data_dict.items()} )
        spike_data = data2.astype('float64')

        # calculate MFR for each electrode
        MFR_mean_list = []
        for elec in spike_data.columns:
            s = spike_data[elec].dropna().tolist()
            MFR_mean_list.append(len(s)/time)
        # add MFR of all electrodes to extracted parameters
        well_list[well]["MFR"] = sum(MFR_mean_list)/len(MFR_mean_list)
        
    
        # ISI
        ISIs = spike_data.diff()
        # calculate mean ISI for each electrode
        ISI_mean_list = []
        for elec in ISIs.columns:
            l = ISIs[elec].dropna().tolist()
            if (len(l) != 0):
                ISI_mean_list.append(sum(l)/len(l))
        # add mean ISI of all electrodes to extracted parameters
        if (len(ISI_mean_list) != 0):
            mean_ISI = sum(ISI_mean_list)/len(ISI_mean_list)
            well_list[well]["Mean ISI"] = mean_ISI
        
            
    # BURST INFO
    # read input
    burst_files = glob.glob(input_folder + '/**/*bursts.csv', recursive=True)
    MBR_mean_list = []  # mean burst rate
    MBdur_list = []   # mean burst duration
    MNS_list = []  # mean number of spikes per burst
    
    for b_file in burst_files:
        well = b_file[-13:-11] 
        # aggregate by well
        dfb = pd.read_csv(b_file)
        bdata = dfb.groupby(["Electrode"]).agg(list)
     
        if not dfb.empty:
            for index, row in bdata.iterrows():  # calculate parameters for individual electrodes
                # mean burst rate
                MBR_mean_list.append(len(row["Number of spikes"])/time)
                # mean burst duration
                MBdur_list.append(sum(row["Burst duration"])/len(row["Burst duration"]))
                # mean number of spikes per burst
                MNS_list.append(sum(row["Number of spikes"])/len(row["Number of spikes"]))
                
            # mean burst rate accross electrodes
            if (len(MBR_mean_list)!= 0):
                MBR = sum(MBR_mean_list)/len(MBR_mean_list)
                well_list[well]["Mean burst rate"] = MBR
            # mean burst duration accross electrodes
            if (len(MBdur_list)!= 0):
                MBdur = sum(MBdur_list)/len(MBdur_list)
                well_list[well]["Mean burst duration"] = MBdur
            # mean number of spikes per burst accross electrodes
            if (len(MNS_list)!= 0):
                MNS = sum(MNS_list)/len(MNS_list)
                well_list[well]["Mean number of spikes per burst"] = MNS
                
            
            sorted_data = dfb.sort_values('First spike time (sec)') # Sort data from smallest electrode burst start time to largest 
            burst_data = sorted_data.reset_index(drop = True) # Reset index in sorted data
            
            # Mean inter burst interval 
            IBeI = burst_data['First spike time (sec)'].diff()
            well_list[well]["Mean IBeI"] = IBeI.mean()
        
        
    # NETWORK BURST INFO
    net_burst_files = glob.glob(input_folder + '/**/*networkBursts.csv', recursive=True)
    
    for n_file in net_burst_files:
        well = n_file[-20:-18]
        
        dfn = pd.read_csv(n_file)
        if not dfn.empty:
            # mean number of spikes per burst
            well_list[well]["Mean number of spikes per network burst"] = dfn["Number of spikes"].mean()
            # mean number of bursts per network burst
            well_list[well]["Mean number of bursts per network burst"] = dfn["Number of electrode bursts"].mean()
            
    
    return dict(sorted(well_list.items()))

    

input_folder = sys.argv[1]  # first command line argument should be input directory


# find spike files in input folder
files = glob.glob(input_folder + '/**/*spike_list.csv', recursive=True)
for inputFile in files:
    # get recording time
    time = time(inputFile)
    # get dict of spike numbers per well
    inputFolder = inputFile[:-25] + '_well_list'
    extr_dict = extract_parameters(inputFolder, time)
    #print(extr_dict)
    
    csv_columns = ['Well', 
                   'Total spikes', 
                   'MFR', 
                   'Mean ISI', 
                   'Mean burst rate', 
                   'Mean burst duration', 
                   'Mean number of spikes per burst', 
                   'Mean IBeI', 
                   'Mean number of spikes per network burst',
                   'Mean number of bursts per network burst']
    
    csv_name = inputFolder + '/extracted_parameters.csv'
    
    with open (csv_name, 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for key, well_dict in extr_dict.items():
            writer.writerow(well_dict)
    
    
    

        
    
