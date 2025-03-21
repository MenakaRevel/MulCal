#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import os
import sys
import re
import warnings
warnings.filterwarnings("ignore")
#================================================================
# read each SE_Diagnostics.csv
# Obs_NMs=['02KC018','02LA027','02LB013','Cedar']
# Obs_NMs = [
#     "02KA015", "02KC015", "02KC018", "02KF010", "02KF011", "02KF015", "02KF017", "02KF018",
#     "02KF020", "02LA024", "02LA026", "02LA027", "02LB006", "02LB007", "02LB008", "02LB009",
#     "02LB013", "02LB018", "02LB020", "02LB022", "02LB031", "02LB032", "02LB033", "02MC001",
#     "02MC026", "02MC028", "02MC036", "02MC037", "Cedar", "Charles", "Hambone", "Lilypond",
#     "NorthDepot", "Radiant", "02MB006"
# ]

ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
ObsList = pd.read_csv(ObsList)
# Obs_NMs = ObsList[ObsList['Obs_NM']!='Burntroot']['Obs_NM'].values
# Obs_NMs = ObsList[ObsList['rivseq']<4]['Obs_NM'].values
# Obs_NMs = ObsList[ObsList['ObsType']=='SF']['Obs_NM'].values
Obs_NMs = ObsList['Obs_NM'].values
# List to store DataFrames
df_list = []

for Obs_NM in Obs_NMs:
    # Read the CSV file
    # df_new = pd.read_csv(f'/home/menaka/scratch/MulCal/{Obs_NM}/processor_0/best/RavenInput/output/SE_Diagnostics.csv')
    df_new = pd.read_csv(f'/home/menaka/scratch/MulCal/{Obs_NM}/best_Raven/output/SE_Diagnostics.csv')
    
    # Remove columns with "Unnamed" in the name
    df_new = df_new.loc[:, ~df_new.columns.str.contains("Unnamed")]

    df_new = df_new.loc[df_new['filename'].str.contains(Obs_NM),:]

    # # Optionally, add a column to track the source of the data
    # df_new['Obs_NM'] = Obs_NM  # Add Obs_NM as an identifier if needed
    
    # Append to the list
    df_list.append(df_new)

# Concatenate all DataFrames at once
df_final = pd.concat(df_list, ignore_index=True)

# Print or save the final DataFrame
print(df_final)

df_final.to_csv("../dat/SiteCal_merged_SE_Diagnostics.csv", index=False)
