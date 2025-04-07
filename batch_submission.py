#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import warnings
import pandas as pd
#=============
# Define the input and output file names
input_file = "submit-MPI-to-server-batch.sh"
output_file = "submit-MPI-to-server-updated.sh"

# "02KF010", "02KF011", 
# Obs_NMs = [
#     "02KF017", "02KF018", "02KF020", 
#     "02LA007", "02LA024", "02LA026", "02LB006", "02LB007", 
#     "02LB017", "02LB022", "02LB031", "02MB006", "02MB010", 
#     "02MC027", "02MC030", "Animoosh", "Burntroot", "Grand", 
#     "Hogan", "LaMuir", "Lavieille", "LittleCauchon", "Loontail", 
#     "Narrowbag", "Timberwolf"
# ]
targetG=1 # max 5
#==========================================================
# Read Obs_NMs
ObsList=pd.read_csv('./dat/GaugeSpecificList.csv')
#==========================================================
# Read CWList
CWList=pd.read_csv('./dat/LakeCWList.csv')
# CWList=CWList.dropna(subset=['Obs_NM'])
#==========================================================
# Obs_NMs = ObsList['Obs_NM'].values
Obs_NMs = ObsList[ObsList['rivseq']==targetG]['Obs_NM'].values
# # # # Obs_NMs = ObsList[ObsList['ObsType']=='SF']['Obs_NM'].values
# # # # Obs_NMs = ObsList[(ObsList['ObsType']=='RS') & (ObsList['rivseq']==1)]['Obs_NM'].values
# # # # Obs_NMs = ObsList[(ObsList['ObsType']=='SF') & (ObsList['rivseq']==1)]['Obs_NM'].values
# print (Obs_NMs)
#==========================================================
if targetG > 1:
    # need to collect Lake CW
    CW_values = {}  # Dictionary to store CW values
    for upLake0 in ObsList[(ObsList['rivseq']==targetG-1) & (ObsList['ObsType']=='RS')]['Obs_NM'].values:
        for upLake in upLake0.split('&'):
            fname="/home/menaka/scratch/MulCal/"+str(upLake)+"/dds_status.out"
            paraList=pd.read_csv(fname, sep='\s+')
            # print (paraList)
            # CW = paraList['w_'+str(upLake)].values[-1]
            CW_values[upLake] = paraList[f'w_{upLake}'].values[-1]  # Store last value
            # CWList.loc[CWList['Obs_NM']==upLake,'cal.CW']=CW
        
        # Update CWList in one operation
        CWList.loc[CWList['Obs_NM'].isin(CW_values.keys()), 'cal.CW'] = CWList['Obs_NM'].map(CW_values)

    CWList.to_csv('./dat/LakeCWList.csv', index=False)

# Read the shell script, modify it, and save the changes
with open(input_file, "r") as file:
    script_content = file.read()

for Obs_NM in Obs_NMs:
    # Replace all occurrences of {Obs_NM} with Obs_NMs
    updated_script = script_content.replace("{Obs_NM}", Obs_NM)

    # Write the updated content to a new file
    with open(output_file, "w") as file:
        file.write(updated_script)

    print(f"Updated script saved as {output_file} for {Obs_NM}")

    # run it
    os.system('sbatch '+output_file)
'''
for Obs_NM in Obs_NMs:
    os.system('sbatch run_best_Raven_MPI.sh '+str(Obs_NM))
'''