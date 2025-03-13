#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 15:48:01 2021

@author: xueerding
"""

import sys
import glob
import os
import csv
import pandas as pd

def spike_sort(inputFile, excluded):
    
    # read input into csv and aggregate by well
    df = pd.read_csv(inputFile, usecols=["Electrode", "Time (s)"])
    df.dropna(inplace=True)
    df2 = df.loc[df["Electrode"].str.fullmatch('\w\d_\d\d')]  # filter for electrode entries
    data = df2.groupby(df2["Electrode"].str[:2]).agg(list)

    # create folder for spike info by well
    outPath = inputFile[:-25] + '_well_list'
    os.mkdir(outPath)
    
    # write csv
    for well, row in data.iterrows():
        # make folder for each well
        outPathWell = outPath + "/" + well
        os.mkdir(outPathWell)
        filename = outPathWell + '/' + well + '_spikes.csv'
        with open (filename, 'w') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames=['Electrode', 'Time (s)'])
            writer.writeheader()
            for elec, time in zip(row['Electrode'], row['Time (s)']):
                if elec not in excluded:
                    writer.writerow({'Electrode': elec, 'Time (s)': time})
            csvfile.close()
    

input_folder = sys.argv[1]  # first command line argument should be input directory
#input_folder = "/Users/xueerding/Desktop/MiCM/data/Extracted_files/Feb132020_ND3439SNCA_WTest3_2h/"
        
# find spike files in input folder
files = glob.glob(input_folder + '/**/*spike_list.csv', recursive=True)
# sort by well for every spike file
for inputFile in files:
    # ask for electrodes to exclude
    excluded = input("Exclude electrodes for file " + inputFile + " (format example: A1_11,A1_34,A3_13): ").split(",")
    spike_sort(inputFile, excluded)