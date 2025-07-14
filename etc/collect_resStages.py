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

# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        print("Usage: extract_reservoir_stages.py <tag>")
        sys.exit(1)

    tag = sys.argv[1]
    base_dir = f"/home/menaka/scratch/MulCal_{tag}"
    output_dir = f"../dat/{tag}"
    mk_dir(output_dir)

    obs_list_path = '/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
    ObsList = pd.read_csv(obs_list_path)
    ObsDir  = '/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
    suffixs = {'SF': 'discharge', 'WL': 'level', 'RS': 'level'}

    df = pd.DataFrame()

    for Obs_NM in ObsList['Obs_NM']:
        best_obj = float('-inf')
        best_trail = 0

        for num in range(1, 11):
            out_path = f"{base_dir}/{Obs_NM}_{num:02d}/dds_status.out"
            obj_val = read_obj_function(out_path)
            if obj_val is not None and obj_val > best_obj:
                best_obj = obj_val
                best_trail = num

        # Skip if no valid DDS outputs
        if best_trail == 0:
            print(f"⚠️ Skipping {Obs_NM}: no valid DDS trail")
            continue

        ObsType = ObsList.loc[ObsList['Obs_NM'] == Obs_NM, 'ObsType'].values[0]
        rvt_file = os.path.join(ObsDir, f"{Obs_NM}_{suffixs[ObsType]}.rvt")
        SubId = read_subid(rvt_file)

        if SubId is None:
            print(f"⚠️ Could not extract SubId for {Obs_NM}")
            continue

        stage_file = f"{base_dir}/{Obs_NM}_{best_trail:02d}/best_Raven/output/SE_ReservoirStages.csv"
        if not os.path.isfile(stage_file):
            print(f"⚠️ Missing file: {stage_file}")
            continue

        try:
            df_stage = pd.read_csv(stage_file)
        except:
            print(f"⚠️ Could not read file: {stage_file}")
            continue

        sub_key = f"sub{SubId} "
        sub_cols = [col for col in df_stage.columns if f"sub{SubId}" in col]

        if not sub_cols:
            print(f"→ sub{SubId} not found in {stage_file} —> no lakes?")
            continue

        # Select columns
        if df.empty:
            cols_to_merge = ['time', 'date', 'hour', 'precip [mm/day]'] + sub_cols
        else:
            cols_to_merge = ['date'] + sub_cols

        df_stage = df_stage[cols_to_merge].copy()

        if df.empty:
            df = df_stage.copy()
        else:
            df = pd.merge(df, df_stage, on='date', how='outer')

    if df.empty:
        print("⚠️ No valid data found.")
        sys.exit(0)

    out_path = os.path.join(output_dir, "SE_ReservoirStages.csv")
    df.to_csv(out_path, index=False)
    print(f"\n✅ Saved merged data to: {out_path}")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()