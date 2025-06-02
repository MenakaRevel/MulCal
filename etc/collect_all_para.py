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
# Obs_NMs = ObsList[ObsList['rivseq']<=4]['Obs_NM'].values
# Obs_NMs = ObsList[ObsList['ObsType']=='SF']['Obs_NM'].values
Obs_NMs = ObsList['Obs_NM'].values
# List to store DataFrames
df_list = []

# Initialize empty DataFrame to collect best parameters
bestParamsDF = pd.DataFrame()

for Obs_NM in Obs_NMs:
    objFun    = float('-inf')
    bestTrail = 0
    paraList  = None
    try:
        fname     = f"/home/menaka/scratch/MulCal/{Obs_NM}_10/dds_status.out"
        paraList0 = pd.read_csv(fname, sep=r'\s+')
    except:
        continue
    #=======================
    for num in range(1, 10+1):
        fname     = f"/home/menaka/scratch/MulCal/{Obs_NM}_{num:02d}/dds_status.out"
        # print (num, fname)
        paraList0   = pd.read_csv(fname, sep=r'\s+')
        # --- Handle w_{Obs_NM} column ---
        if f"w_{Obs_NM}" in paraList0.columns:
            paraList0 = paraList0.rename(columns={f"w_{Obs_NM}": "CW"})
        else:
            paraList0["CW"] = np.nan
        # # Add Obs_NM
        # paraList0['Obs_NM'] = Obs_NM
        # ---------------------------------
        current_obj = -paraList0['OBJ._FUNCTION'].iloc[-1]
        if current_obj > objFun:
            objFun    = current_obj
            bestTrail = num
            paraList  = paraList0.iloc[[-1]]

    print (paraList)
    if paraList is not None:
        paraList = paraList.copy()
        paraList['Obs_NM'] = Obs_NM
        bestParamsDF = pd.concat([bestParamsDF, paraList], ignore_index=True)

print (bestParamsDF)

cols = ["Obs_NM"] + [col for col in bestParamsDF.columns if col != "Obs_NM"]
bestParamsDF = bestParamsDF[cols]
bestParamsDF.to_csv("../dat/SiteCal_merged_SE_parameter_new.csv", index=False)
