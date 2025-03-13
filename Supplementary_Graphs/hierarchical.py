#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 11:04:50 2021

@author: xueerding
"""
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot  as plt

inputFile = sys.argv[1]  # first field should be input file path

# hierarchical clustering by plate
data = pd.read_excel(inputFile, sheet_name="Combined by plate", header=4, index_col=[0,1], skiprows=[5,])

data_to_clus = data[['Total spikes', 'MFR', 'Number of bursts', 
                     'Number of network bursts', 'Synchrony index']]

groups = data.index.get_level_values(0)
print(groups.unique())
lut = dict(zip(groups.unique(), ['indianred', 'gold', 'limegreen', 
                                 'deepskyblue', 'slateblue', 'violet']))
print(lut)
row_colors = groups.map(lut)
data_clusterGrid = sns.clustermap(data_to_clus, standard_scale=1, figsize=(12, 10), 
                                  dendrogram_ratio=(.3, .3), cbar_pos=(0, .05, .03, .3), 
                                  row_colors=row_colors )


# hierarchical clustering by cell line
data2 = pd.read_excel(inputFile, sheet_name="Combined by line", header=4, index_col=[0,1,2], skiprows=[5,])

data_to_clus2 = data2[['Total spikes', 'MFR', 'Number of bursts', 
                     'Number of network bursts', 'Synchrony index']]

groups2 = data2.index.get_level_values(0)
print(groups2.unique())
lut2 = dict(zip(groups2.unique(), ['firebrick', 'darkorange', 'gold', 'springgreen', 
                                   'deepskyblue', 'slateblue', 'purple']))
print(lut2)
row_colors2 = groups2.map(lut2)
data_clusterGrid2 = sns.clustermap(data_to_clus2, standard_scale=1, figsize=(12, 10), 
                                   dendrogram_ratio=(.3, .3), cbar_pos=(0, .05, .03, .3),
                                   row_colors=row_colors2 )


# hierarchical clustering by plate for syn mutants only
data3 = pd.read_excel(inputFile, sheet_name="Synuclein Triplication", header=4, index_col=[0,1], skiprows=[5,])

data_to_clus3 = data3[['Total spikes', 'MFR', 'Number of bursts', 
                     'Number of network bursts', 'Synchrony index']]

groups3 = data3.index.get_level_values(0)
print(groups3.unique())
lut3 = dict(zip(groups3.unique(), ['lime', 'deepskyblue', 'slateblue', 
                                   'orchid', 'hotpink']))
print(lut3)
row_colors3 = groups3.map(lut3)
data_clusterGrid3 = sns.clustermap(data_to_clus3, standard_scale=1, figsize=(12, 10), 
                                   dendrogram_ratio=(.3, .3), cbar_pos=(0, .05, .03, .3),
                                   row_colors=row_colors3 )


plt.show()
#data_clusterGrid3.fig.suptitle('Hierarchical clustering of mutant organoids')

