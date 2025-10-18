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

suffixs = {
    'SF':'discharge',
    'WL':'level',
    'RS':'level'
}
#====================================================================================================
def mk_dir(path):
    os.makedirs(path, exist_ok=True)

#====================================================================================================
def read_subid(fname):
    """Extracts the station ID from the ObservationData line."""
    with open(fname, 'r') as f:
        text = f.read()
    match = re.search(r'ObservationData\s+\S+\s+(\d+)', text)
    return str(match.group(1)) if match else '0'

#====================================================================================================
def read_last_obj_function(fname):
    """Efficiently read the last line of dds_status.out to get the objective function."""
    try:
        with open(fname, 'rb') as f:
            f.seek(-1024, os.SEEK_END)  # read last ~1KB block
            lines = f.readlines()
        last_line = lines[-1].decode('utf-8').strip()
        obj_val = float(last_line.split()[-1])
        return -obj_val
    except Exception:
        return None

#====================================================================================================
def main():
    # Validate arguments
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <tag> <odir>")
        sys.exit(1)

    reg  = sys.argv[1]
    tag  = sys.argv[2]
    odir = sys.argv[3]

    base_dir   = os.path.join(odir,tag)
    output_dir = os.path.join("../dat/",tag)

    mk_dir(output_dir)

    # Define paths and constants
    obs_dir        = f'/home/menaka/projects/def-btolson/menaka/{reg}region/OstrichRaven/RavenInput/obs'
    obs_list_file  = f'/home/menaka/projects/def-btolson/menaka/MulCal/dat/{reg}/GaugeSpecificList.csv'
    obs_list_subid = f'/home/menaka/projects/def-btolson/menaka/MulCal/dat/{reg}/GaugeSubIdList.csv'
    suffixs = {'SF': 'discharge', 'WL': 'level', 'RS': 'level'}

    # Load observation list
    ObsList = pd.read_csv(obs_list_file)
    Obs_NMs = ObsList['Obs_NM'].values
    obs_type_dict = dict(zip(ObsList['Obs_NM'], ObsList['ObsType']))

    # Load subbasin list
    SubList = pd.read_csv(obs_list_subid)
    # Obs_NMs = ObsList['Obs_NM'].values
    obs_subid_dict = dict(zip(SubList['Obs_NM'], SubList['UpSubIds'].str.split('&')))

    df_list = []
    core_cols = ['time', 'date', 'hour', 'precip [mm/day]']

    for Obs_NM in Obs_NMs:
        bestTrail, objFun = 0, float('-inf')

        # Loop over DDS outputs to find best trail
        for num in range(1, 11):
            fname = f"{base_dir}/{Obs_NM}_{num:02d}/dds_status.out"
            obj   = read_last_obj_function(fname)
            if obj is not None and obj > objFun:
                objFun = obj
                bestTrail = num

        if bestTrail == 0:
            print(f"Skipping {Obs_NM}: no valid DDS trails.")
            continue

        # Get SubId
        ObsType  = obs_type_dict[Obs_NM]
        obs_file = os.path.join(obs_dir, f"{Obs_NM}_{suffixs[ObsType]}.rvt")
        SubId    = str(ObsList[ObsList['Obs_NM']==Obs_NM]['SubId'].values[0])      #read_subid(obs_file)
        SubId_1  = SubList[SubList['Obs_NM']==Obs_NM]['SubId'].values[0]
        # lSubId   = obs_subid_dict[Obs_NM]
        UpSubIds = obs_subid_dict[Obs_NM] 
        
        # remove the other observation subid
        oSubId   = [str(x) for x in ObsList[ObsList['Obs_NM'] != Obs_NM]['SubId'].values]
        UpSubIds = list(set(set(UpSubIds) | set([SubId]) - set(oSubId)))

        # 
        # BasinType=ObsList[ObsList['Obs_NM']==Obs_NM]['Type'].values[0]
        # if BasinType == 'Upstream':
        #     UpObsNMList = 'None'
        #     UpObsTypes  = ['None']
        #     UpSubIds    = ['None']
        # else:
        #     UpObsNMList = ObsList[ObsList['Obs_NM']==Obs_NM]['UpGauges'].values[0]
        #     # print (UpObsNMList)
        #     UpObsTypes  = [ObsList[ObsList['Obs_NM']==gau]['ObsType'].values[0] for gau in UpObsNMList.split('&')]
        #     UpSubIds    = [read_subid(os.path.join(obs_dir,UpObs_NM+'_'+suffixs[ObsType]+'.rvt')) for UpObs_NM, ObsType in zip(UpObsNMList.split('&'),UpObsTypes)]

        # Read SE_Hydrograph
        hydro_file = f"{base_dir}/{Obs_NM}_{bestTrail:02d}/best_Raven/output/{reg}_WaterLevels.csv"
        try:
            df_hyd = pd.read_csv(hydro_file)
        except Exception as e:
            print(f"\tFailed to read {hydro_file}: {e}")
            continue

        # print ("="*20)
        # print (Obs_NM, SubId, SubId_1)
        # print ('SubId:',SubId)
        # print ('UpSubIds:',UpSubIds)
        # Filter columns
        # sub_cols = df_hyd.filter(regex=f"sub{SubId}").columns.tolist()
        sub_cols = df_hyd.filter(regex=r"^sub.*").columns.tolist()
        unique_sub_cols = list({re.match(r"sub\d+", col).group(0)[3::] for col in sub_cols})
        # print ('unique_sub_cols:',unique_sub_cols)
        # Combine both filtering steps into one comprehension
        # sub_cols = [
        #     col for col in sub_cols
        #     if (re.search(r'\d+', col).group() in lSubId)
        #     and (re.search(r'\d+', col).group() not in UpSubIds)
        # ]
        # # Assuming lSubId and UpSubIds are lists of strings
        sub_cols = [
            col for col in sub_cols
            if col.startswith('sub') and re.search(r'\d+', col).group() in UpSubIds
        ]
        if not sub_cols:
            print(f"\tsub{SubId} not found in {hydro_file}")
            continue

        unique_sub_cols = list({re.match(r"sub\d+", col).group(0) for col in sub_cols})

        if not df_list:
            cols = core_cols + sub_cols
        else:
            cols = ['date'] + sub_cols

        df_hyd = df_hyd.loc[:, cols]
        df_list.append(df_hyd)

        print(f"Processed: {Obs_NM} (Trail {bestTrail}, SubId {SubId}, # of simulation {len(unique_sub_cols)} | {len(sub_cols)})")

    # Merge all hydrographs on 'date'
    if not df_list:
        print("No Water Levels to merge.")
        sys.exit(0)

    df = df_list[0]
    for df_next in df_list[1:]:
        df = pd.merge(df, df_next, on='date', how='outer', suffixes=('_1', '_2'))

    mk_dir(output_dir)
    df.to_csv(f"{output_dir}/{reg}_WaterLevels.csv", index=False)
    print(f"Saved merged Water Levels to {output_dir}/{reg}_WaterLevels.csv")

#====================================================================================================
if __name__ == "__main__":
    main()