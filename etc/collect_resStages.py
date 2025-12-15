#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
def mk_dir(path):
    os.makedirs(path, exist_ok=True)

def read_subid(rvt_path):
    """Extracts SubId from .rvt file."""
    if not os.path.isfile(rvt_path):
        return None
    try:
        with open(rvt_path, 'r') as f:
            content = f.read()
        match = re.search(r'ObservationData\s+\S+\s+(\d+)', content)
        return int(match.group(1)) if match else None
    except:
        return None

def read_obj_function(out_path):
    """Returns objective function from DDS output."""
    if not os.path.isfile(out_path):
        return None
    try:
        df = pd.read_csv(out_path, sep=r'\s+')
        if df.empty:
            return None
        return -df['OBJ._FUNCTION'].iloc[-1]
    except:
        return None
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

# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: "+sys.argv[0]+" <tag> <odir>")
        sys.exit(1)

    reg  = sys.argv[1]
    tag  = sys.argv[2]
    odir = sys.argv[3]

    base_dir   = os.path.join(odir,tag)
    output_dir = os.path.join("../dat", reg, tag)

    mk_dir(output_dir)

    # obs_list_path = '/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
    # ObsList = pd.read_csv(obs_list_path)
    # ObsDir  = '/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
    # suffixs = {'SF': 'discharge', 'WL': 'level', 'RS': 'level'}

    obs_dir        = f'/home/menaka/projects/def-btolson/menaka/{reg}region/OstrichRaven/RavenInput/obs'
    obs_list_file  = f'/home/menaka/projects/def-btolson/menaka/MulCal/dat/{reg}/GaugeSpecificList.csv'
    obs_list_subid = f'/home/menaka/projects/def-btolson/menaka/MulCal/dat/{reg}/GaugeSubIdList.csv'
    suffixs        = {'SF': 'discharge', 'WL': 'level', 'RS': 'level'}

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

    df = pd.DataFrame()

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

        if SubId is None:
            print(f"⚠️ Could not extract SubId for {Obs_NM}")
            continue

        stage_file = f"{base_dir}/{Obs_NM}_{bestTrail:02d}/best_Raven/output/{reg}_ReservoirStages.csv"
        if not os.path.isfile(stage_file):
            print(f"⚠️ Missing file: {stage_file}")
            continue

        try:
            df_stage = pd.read_csv(stage_file)
        except:
            print(f"⚠️ Could not read file: {stage_file}")
            continue

        sub_key = f"sub{SubId} "
        # sub_cols = [col for col in df_stage.columns if f"sub{SubId}" in col]
        sub_cols = df_stage.filter(regex=r"^sub.*").columns.tolist()
        unique_sub_cols = list({re.match(r"sub\d+", col).group(0)[3::] for col in sub_cols})
        print ('unique_sub_cols:',unique_sub_cols)
        
        # # Assuming lSubId and UpSubIds are lists of strings
        sub_cols = [
            col for col in sub_cols
            if col.startswith('sub') and re.search(r'\d+', col).group() in UpSubIds
        ]


        # Check if any column contains the Obs_NM string
        Obs_NM_columns = [col for col in df_stage.columns if Obs_NM in col]

        if not Obs_NM_columns:
            print(f"\tNo columns found for Obs_NM {Obs_NM} in {stage_file}")
            continue

        # add those columns to sub_cols
        sub_cols.extend(Obs_NM_columns)

        if not sub_cols:
            print(f"→ sub{SubId} not found in {stage_file} —> no lakes?")
            continue

        sub_like_cols = [col for col in df_stage.columns if col.lower().startswith('sub')]
        unique_sub_cols = list({m.group(0) for col in sub_like_cols if (m := re.match(r"sub\d+", col.lower()))})
        unique_sub_cols += Obs_NM_columns if Obs_NM_columns else []

        # Select columns
        if df.empty:
            cols_to_merge = core_cols + sub_cols
        else:
            cols_to_merge = ['date'] + sub_cols

        df_stage = df_stage[cols_to_merge].copy()

        if df.empty:
            df = df_stage.copy()
        else:
            df = pd.merge(df, df_stage, on='date', how='outer')

        print(f"Processed: {Obs_NM} (Trail {bestTrail}, SubId {SubId}, # of simulation {len(unique_sub_cols)})")

    if df.empty:
        print("⚠️ No valid data found.")
        sys.exit(0)

    out_path = os.path.join(output_dir, f"{reg}_ReservoirStages.csv")
    df.to_csv(out_path, index=False)
    print(f"\n✅ Saved merged data to: {out_path}")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()