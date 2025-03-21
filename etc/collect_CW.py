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
CWList=pd.read_csv('../dat/LakeCWList.csv')
# CWList.drop(columns=['SubBasinID','HRUID'],inplace=True)
CWList.rename(columns={'Reservoir':'HylakId'},inplace=True)
print (CWList)
#================================================================
# add column loc.CW
CWList.rename(columns={'cal.CW':'loc.CW'},inplace=True)
#================================================================
# add column glb1.CW
ddss =pd.read_csv('/home/menaka/scratch/SEregion/MPI_SE_GLB_01/dds_status.out', sep='\s+')
CWList['glb1.CW']=CWList['ini.CW']*ddss['k_multi'].values[-1]

#================================================================
# add column glb2.CW
ddss =pd.read_csv('/home/menaka/scratch/SEregion/MPI_SE_GLB_02/dds_status.out', sep='\s+')
CWList['glb2.CW']=CWList['ini.CW']
# add column glb3.CW
ddss =pd.read_csv('/home/menaka/scratch/SEregion/MPI_SE_GLB_03/dds_status.out', sep='\s+')
CWList['glb3.CW']=CWList['ini.CW']
# for Obs_NM in CWList['Obs_NM'].dropna().values:
#     print (Obs_NM, ddss['w_'+str(Obs_NM)].values[-1])
#     CWList.loc[CWList['Obs_NM']==Obs_NM,'glb2.CW']=ddss['w_'+str(Obs_NM)].values[-1]
# Drop NaN values and create a mapping of Obs_NM to the latest values in ddss
obs_values = CWList['Obs_NM'].dropna().unique()  # Use unique() to avoid redundant calculations
latest_values = {Obs_NM: ddss[f'w_{Obs_NM}'].values[-1] for Obs_NM in obs_values}

# Print values efficiently
for Obs_NM, value in latest_values.items():
    print(Obs_NM, value)

# Update CWList efficiently using map
CWList.loc[CWList['Obs_NM'].notna(), 'glb2.CW'] = CWList['Obs_NM'].map(latest_values)

CWList.loc[CWList['Obs_NM'].isnull(),'glb2.CW']=CWList['ini.CW']*ddss['k_multi'].values[-1]

# Update CWList efficiently using map
CWList.loc[CWList['Obs_NM'].notna(), 'glb3.CW'] = CWList['Obs_NM'].map(latest_values)

CWList.loc[CWList['Obs_NM'].isnull(),'glb3.CW']=CWList['ini.CW']*ddss['k_multi'].values[-1]

print (CWList)

CWList.to_csv('../dat/LakeCWCalibratedSummary.csv',index=False)