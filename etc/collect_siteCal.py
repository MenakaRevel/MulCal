#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

def mk_dir(path):
    os.makedirs(path, exist_ok=True)

def read_obj_function(out_path):
    """Return last negative OBJ._FUNCTION value or None if file missing/unreadable."""
    if not os.path.isfile(out_path):
        return None
    try:
        df = pd.read_csv(out_path, sep=r'\s+')
        if df.empty:
            return None
        return -df['OBJ._FUNCTION'].iloc[-1]
    except:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: extract_se_diagnostics.py <tag>")
        sys.exit(1)

    tag = sys.argv[1]
    base_dir = f"/home/menaka/scratch/MulCal_{tag}"
    output_dir = f"../dat/{tag}"
    mk_dir(output_dir)

    obs_list_path = '/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
    ObsList = pd.read_csv(obs_list_path)
    Obs_NMs = ObsList['Obs_NM'].values

    df_list = []

    for Obs_NM in Obs_NMs:
        best_obj = float('-inf')
        best_trail = 0

        # Find best trail by highest OBJ._FUNCTION
        for num in range(1, 11):
            out_path = f"{base_dir}/{Obs_NM}_{num:02d}/dds_status.out"
            obj_val = read_obj_function(out_path)
            if obj_val is not None and obj_val > best_obj:
                best_obj = obj_val
                best_trail = num

        if best_trail == 0:
            print(f"⚠️ No valid DDS run found for {Obs_NM}, skipping.")
            continue

        diag_path = f"{base_dir}/{Obs_NM}_{best_trail:02d}/best_Raven/output/SE_Diagnostics.csv"
        if not os.path.isfile(diag_path):
            print(f"⚠️ Missing diagnostics file {diag_path}, skipping.")
            continue

        try:
            df_new = pd.read_csv(diag_path)
        except Exception as e:
            print(f"⚠️ Could not read {diag_path}: {e}, skipping.")
            continue

        # Remove any 'Unnamed' columns
        df_new = df_new.loc[:, ~df_new.columns.str.contains('^Unnamed')]

        # Keep only rows where 'filename' contains the Obs_NM string
        df_new = df_new[df_new['filename'].str.contains(Obs_NM, na=False)]

        df_list.append(df_new)

    if not df_list:
        print("⚠️ No diagnostics data collected, exiting.")
        sys.exit(0)

    df_final = pd.concat(df_list, ignore_index=True)

    out_file = os.path.join(output_dir, "SE_Diagnostics.csv")
    df_final.to_csv(out_file, index=False)
    print(f"\n✅ Saved merged diagnostics to {out_file}")

if __name__ == "__main__":
    main()