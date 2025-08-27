#! /usr/bin/python
#! utf+8
'''
check_lake_amplitude.py --> lake water level 
- Check outlier annual mean amplitude 
- Change CW lake to large value 9999m of outliers
- Check KGE {1. if KGE change singnifantly recalibrate}
'''
import pandas as pd 
import numpy as np 
import os
import sys
import re
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")
#===================
expName = sys.argv[1]
thrAmp  = float(sys.argv[2])
outdir  = sys.argv[3]  # /home/menaka/scratch/MulCal/out
start_dt= sys.argv[4]  # start date for evaluation
end_dt  = sys.argv[5]  # end date for evaluation
#===================
# 1. read the best calibrated trail {ModelName}_ReservoirStages.csv
# ------------------------------------------------------------------ #
# 1a.  Read data tables                                               #
# ------------------------------------------------------------------ #
ObsList = pd.read_csv("../dat/GaugeSpecificList.csv")
CWList  = pd.read_csv("../dat/LakeCWList.csv")

Obs_NMs = ObsList["Obs_NM"].values

lake_outliers = []
lake_outlier_dict = {}
for obs in Obs_NMs:
    best_obj, best_paras   = float("-inf"), None
    lake_outlier_dict[obs] = []
    for n in range(1, 10+1):
        status = Path(f"{outdir}/{expName}/{obs}_{n:02d}/dds_status.out")
        try:
            df = pd.read_csv(status, sep=r"\s+")
            obj = -df["OBJ._FUNCTION"].iloc[-1]
            if obj > best_obj:
                best_n, best_obj, best_paras = n, obj, df
        except Exception:
            print("  • missing file:", status)


    # go to ReservoirStage.csv
    fname          = Path(f"{outdir}/{expName}/{obs}_{best_n:02d}/best_Raven/output/SE_ReservoirStages.csv")
    df_res         = pd.read_csv(fname)

    # Convert to datetime and extract year
    df_res['date'] = pd.to_datetime(df_res['date'])
    df_res['year'] = df_res['date'].dt.year

    # 2002-10-01 - 2018-09-30
    # Define date range
    start_date = pd.Timestamp(start_dt)
    end_date   = pd.Timestamp(end_dt)

    # Filter dataframe
    df_res = df_res[(df_res['date'] >= start_date) & (df_res['date'] <= end_date)]
    
    # print (df_res.columns)
    # get lake subbasins *Sub_{SubID}
    lake_cols = [col for col in df_res.columns if col.startswith('sub') and 'observed' not in col]
    
    #
    #===================
    # 2. Assess each lake amplitude {ModelName}_ReservoirStages.csv
    # ------------------------------------------------------------------ #
    if lake_cols:
        lake_yearly_amp = df_res.groupby('year')[lake_cols].agg(lambda x: x.max() - x.min())
        lake_mean_amp   = lake_yearly_amp.mean().reset_index()
        lake_mean_amp.columns = ['SubId', 'mean_annual_amplitude']
        outlier_lakes   = lake_mean_amp[lake_mean_amp['mean_annual_amplitude'] > thrAmp]['SubId'].values
        if len(outlier_lakes) > 0:
            print (
                f"{obs}"+
                f"\t The mean annual amplitutde is > {thrAmp:.2f} of these lakes :"+
                "\n\t\t".join(outlier_lakes))
            lake_outliers += outlier_lakes.tolist()
            lake_outlier_dict[obs] += outlier_lakes.tolist()
    #     else:
    #         print (f"No outlier lakes in the sub-region {obs}")
    # else:
    #     print (f"No lakes in the sub-region {obs}")

# print (
#     f'Outlier lakes > {thrAmp:.2f} are :\n'+
#     "\n\t".join(lake_outliers)+
#     "\n# Outlier lakes: "+
#     str(len(lake_outliers))
#     )

# print (lake_outlier_dict)

# for key, values in lake_outlier_dict.items():
#     if values:  # checks if value is non-empty
#         print(key)
#         for value in values: print(value[3:])

# Convert dictionary to a DataFrame
df = pd.DataFrame(
    [(k, '&'.join(s.strip().replace('sub', '') for s in v)) for k, v in lake_outlier_dict.items()],
    columns=['ObsNm', 'SubId']
)

# Replace empty strings with NaN
df['SubId']=df['SubId'].replace('', np.nan).astype('Int64')

if df.dropna().empty:
    print (f"No lakes have abnorml amplitudes (> {thrAmp:.2f})")
else:
    # print (df.dropna())
    print (f"{len(df.dropna()):d} lakes have abnorml amplitudes (> {thrAmp:.2f})")
    print ("Check the KGE of above lakes by changing the lake CW to 9999.0")

df.dropna().to_csv(f'../dat/{expName}/outliler_lakes_amplitude.csv', index=False)