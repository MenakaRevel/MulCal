#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import os
import sys
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
def mk_dir(path):
    os.makedirs(path, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
def read_last_dds_obj(fname):
    """
    Return (objective_value, last_row_of_dataframe) or (None, None)
    if the file does not exist or cannot be read.
    """
    if not os.path.isfile(fname):
        return None, None          # ← missing file handled here
    try:
        df = pd.read_csv(fname, sep=r'\s+')
        if df.empty:
            return None, None
        obj_val = -df['OBJ._FUNCTION'].iloc[-1]
        return obj_val, df.iloc[[-1]].copy()
    except Exception:
        return None, None          # ← unreadable file handled here

# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        print("Usage: extract_parameters.py <tag>")
        sys.exit(1)

    tag = sys.argv[1]
    base_dir   = f"/home/menaka/scratch/MulCal_{tag}"
    output_dir = f"../dat/{tag}"
    mk_dir(output_dir)

    obs_list_file = '/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
    ObsList  = pd.read_csv(obs_list_file)
    Obs_NMs  = ObsList['Obs_NM'].values

    bestParamsDF = pd.DataFrame()

    for Obs_NM in Obs_NMs:
        best_obj, best_row = float('-inf'), None

        for num in range(1, 11):
            fname = f"{base_dir}/{Obs_NM}_{num:02d}/dds_status.out"
            obj_val, row = read_last_dds_obj(fname)

            if row is None:                   # ← skip missing/unreadable trail
                continue

            if f"w_{Obs_NM}" in row.columns:
                row.rename(columns={f"w_{Obs_NM}": "CW"}, inplace=True)
            else:
                row["CW"] = np.nan

            if obj_val > best_obj:
                best_obj, best_row = obj_val, row

        if best_row is not None:              # ← skip gauge entirely if all trails missing
            best_row["Obs_NM"] = Obs_NM
            bestParamsDF = pd.concat([bestParamsDF, best_row], ignore_index=True)

    if bestParamsDF.empty():
        print("No valid parameters found.")
        sys.exit(0)

    cols = ["Obs_NM"] + [c for c in bestParamsDF.columns if c != "Obs_NM"]
    bestParamsDF = bestParamsDF[cols]

    out_file = os.path.join(output_dir, "SE_parameters.csv")
    bestParamsDF.to_csv(out_file, index=False)
    print(f"\n✅ Saved best parameters to {out_file}")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()