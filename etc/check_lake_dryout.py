#! /usr/bin/python
#! utf+8
'''
check_lake_dryout.py --> check the lake stage < -depth
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
thrDry  = float(sys.argv[2])
outdir  = sys.argv[3]  # /home/menaka/scratch/MulCal/out
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
    # print (df_res.columns)
    # get lake subbasins *Sub_{SubID}
    lake_cols = [col for col in df_res.columns if col.startswith('sub') and 'observed' not in col]
    
    #
    #===================
    # 2. Assess each lake dry out {ModelName}_ReservoirStages.csv
    # ------------------------------------------------------------------ #
    if lake_cols:
        outlier_lakes = []
        max_depth_map = CWList.set_index('SubBasinID')['MaxDepth'].to_dict()

        for lake in lake_cols:
            SubId = int(lake.strip().replace('sub', ''))
            max_depth = max_depth_map.get(SubId, None)

            if max_depth is None:
                max_depth = 9999.0
                # continue  # skip if no MaxDepth for this SubId

            n_dry = (df_res[lake] < -max_depth).sum()

            if n_dry > thrDry:
                outlier_lakes.append(SubId)

        lake_outliers += outlier_lakes
        lake_outlier_dict[obs] += outlier_lakes

# Convert dictionary to a DataFrame
df = pd.DataFrame(
    [(k, '&'.join(s.strip().replace('sub', '') for s in v)) for k, v in lake_outlier_dict.items()],
    columns=['ObsNm', 'SubId']
)

# Replace empty strings with NaN
df['SubId']=df['SubId'].replace('', np.nan).astype('Int64')

if df.dropna().empty:
    print (f"No lakes dried out (> {thrDry:.0f} days)")
else:
    print (df.dropna())
    print (f"{len(df.dropna()):d} lakes dried out (> {thrAmp:.2f} days)")
    print ("Check the KGE of above lakes by changing the lake CW to 9999.0")

df.dropna().to_csv(f'../dat/{expName}/outliler_lakes_dryout.csv', index=False)    