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
data = pd.read_excel(inputFile, sheet_name="Example Data", header=4, index_col=[0,1], skiprows=[5,])

data_to_clus = data[['NB duration', 'Burst duration', 'Spikes per burst', 'Spikes per NB' ]]

groups = data.index.get_level_values(0)
print(groups.unique())
lut = dict(zip(groups.unique(), ['indianred', 'gold', 'limegreen', 
                                 'deepskyblue', 'slateblue', 'violet']))
print(lut)
row_colors = groups.map(lut)
data_clusterGrid = sns.clustermap(data_to_clus, standard_scale=1, figsize=(12, 10), 
                                  dendrogram_ratio=(.3, .3), cbar_pos=(0, .05, .03, .3), 
                                  row_colors=row_colors )



plt.show()
#data_clusterGrid3.fig.suptitle('Hierarchical clustering of mutant organoids')

