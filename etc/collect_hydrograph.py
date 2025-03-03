#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys
import os
import re
import warnings
warnings.filterwarnings("ignore")
#================================================================
def read_subid(fname):
    """Extracts the station ID from the ObservationData line, handling variable keywords."""
    with open(fname, 'r') as f:
        text=f.read()

    match = re.search(r'ObservationData\s+\S+\s+(\d+)', text)
    return int(match.group(1)) if match else 0
#================================================================
ObsDir='/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
#================================================================
suffixs = {
    'SF':'discharge',
    'WL':'level',
    'RS':'level'
}
#================================================================
# read each SE_Diagnostics.csv
Obs_NMs=['02KF010','02KF013']
# Obs_NMs = [
#     "02KA015", "02KC015", "02KC018", "02KF010", "02KF015", 
#     "02KF017", "02KF018", "02KF020", "02LA027", "02LB008", 
#     "02LB009", "02LB013", "02LB018", "02LB020", "02LB032", 
#     "02LB033", "02MC001", "02MC026", "02MC028", "02MC036", 
#     "02MC037", "Cedar", "Charles", "Hambone", "Lilypond", 
#     "NorthDepot", "Radiant", "02KF011"
# ]

# dat/GaugeSpecificList.csv
ObsList=pd.read_csv('../dat/GaugeSpecificList.csv')
df=pd.DataFrame()

for i, Obs_NM in enumerate(Obs_NMs):
    print (Obs_NM)
    ObsType=ObsList[ObsList['Obs_NM']==Obs_NM]['ObsType'].values[0] #read_cal_gagues("./RavenInput")[Obs_NM]
    Obsrvt=os.path.join(ObsDir,Obs_NM+'_'+suffixs[ObsType]+'.rvt')
    SubId=read_subid(Obsrvt)
    # read SE_Hydrograph
    fname=f"/home/menaka/scratch/MulCal/{Obs_NM}/best_Raven/output/SE_Hydrographs.csv"
    df_hyd=pd.read_csv(fname)
    print (df_hyd.columns)

    # Select required columns
    cols_to_merge = ['date', f'sub{SubId} [m3/s]', f'sub{SubId} (observed) [m3/s]']
    df_hyd = df_hyd.loc[:, cols_to_merge].copy()

    # Merge with df
    if i == 0:
        print ("df is None")
        df = df_hyd.copy()  # Initialize df with the first dataset
    else:
        print ("df is NOT None")
        df = pd.merge(df, df_hyd, on='date', how='outer')  # Use 'outer' to keep all data

print (df)
df.to_csv("../dat/SiteCal_merged_SE_Hydrographs.csv", index=False)