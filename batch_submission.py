#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import warnings
import pandas as pd
#=============
# Define the input and output file names
input_file = "submit-MPI-to-server-batch_jobarray.sh"
output_file = "submit-MPI-to-server-updated_jobarray.sh"

# "02KF010", "02KF011", 
# Obs_NMs = [
#     "02KF017", "02KF018", "02KF020", 
#     "02LA007", "02LA024", "02LA026", "02LB006", "02LB007", 
#     "02LB017", "02LB022", "02LB031", "02MB006", "02MB010", 
#     "02MC027", "02MC030", "Animoosh", "Burntroot", "Grand", 
#     "Hogan", "LaMuir", "Lavieille", "LittleCauchon", "Loontail", 
#     "Narrowbag", "Timberwolf"
# ]
targetG=int(sys.argv[1]) # max 5
CWindv=sys.argv[2] #'False' #True
BiasCorr=sys.argv[3] #'False'
calCatRoute=sys.argv[4] #'False'
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
    # for upLake0 in ObsList[(ObsList['rivseq']==targetG-1) & (ObsList['ObsType']=='RS')]['Obs_NM'].values:
    for upLake0 in CWList['Obs_NM'].dropna().values:
        for upLake in upLake0.split('&'):
            if upLake not in ObsList[ObsList['rivseq']==targetG-1]['Obs_NM'].values:
                continue
            objFun    = float('-inf')
            bestTrail = 0
            paraList  = None
            #=======================
            for num in range(1, 10+1):
                fname     = f"/home/menaka/scratch/MulCal/{upLake}_{num:02d}/dds_status.out"
                paraList0 = pd.read_csv(fname, sep=r'\s+')
                print (fname,paraList0)
                current_obj = -paraList0['OBJ._FUNCTION'].iloc[-1]
                if current_obj > objFun:
                    objFun    = current_obj
                    bestTrail = num
                    paraList  = paraList0
            # print (paraList)
            # CW = paraList['w_'+str(upLake)].values[-1]
            if CWindv == 'True':
                CW_values[upLake] = paraList[f'w_{upLake}'].values[-1]  # Store last value
            else:
                CW_values[upLake] = paraList['k_multi'].values[-1]*CWList[CWList['Obs_NM']==upLake]['ini.CW'].values[0]

            # CWList.loc[CWList['Obs_NM']==upLake,'cal.CW']=CW
        
        # Update CWList in one operation
        CWList.loc[CWList['Obs_NM'].isin(CW_values.keys()), 'cal.CW'] = CWList['Obs_NM'].map(CW_values)

    CWList.to_csv('./dat/LakeCWList.csv', index=False)

# Read the shell script, modify it, and save the changes
with open(input_file, "r") as file:
    script_content = file.read()

for Obs_NM in Obs_NMs:
    updated_script = script_content
    print ('+++++'*20)
    print (Obs_NM)
    print ('+++++'*20)
    # Replace all occurrences of {Obs_NM} with Obs_NMs
    updated_script = updated_script.replace("{Obs_NM}", Obs_NM)
    # print (updated_script)

    # Replace all occurrences of {CWindv} with CWindv
    updated_script = updated_script.replace("{CWindv}", CWindv)
    # print (updated_script)

    # Replace all occurrences of {BiasCorr} with BiasCorr
    updated_script = updated_script.replace("{BiasCorr}", BiasCorr)
    # print (updated_script)

    # Replace all occurrences of {calCatRoute} with calCatRoute
    updated_script = updated_script.replace("{calCatRoute}", calCatRoute)
    # print (updated_script)

    # Write the updated content to a new file
    # output_file = f"submit-MPI-to-server-{Obs_NM}.sh"
    with open(output_file, "w") as file:
        file.write(updated_script)

    print(f"Updated script saved as {output_file} for {Obs_NM}")

    print ('\tsbatch '+output_file)

    # run it
    os.system('sbatch '+output_file)

'''
targetG = 1
Obs_NMs = ObsList[ObsList['rivseq']<=targetG]['Obs_NM'].values
for Obs_NM in Obs_NMs:
    for num in range(1,10+1):
        print ('sbatch run_best_Raven_MPI.sh   '+str(Obs_NM)+'   %02d'%(num))
        os.system('sbatch run_best_Raven_MPI.sh   '+str(Obs_NM)+'   %02d'%(num))
'''
