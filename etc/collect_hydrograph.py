#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys
import os
import re
import warnings
warnings.filterwarnings("ignore")

#====================================================================================================
def mk_dir(path):
    os.makedirs(path, exist_ok=True)

#====================================================================================================
def read_subid(fname):
    """Extracts the station ID from the ObservationData line."""
    with open(fname, 'r') as f:
        text = f.read()
    match = re.search(r'ObservationData\s+\S+\s+(\d+)', text)
    return int(match.group(1)) if match else 0

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

    tag  = sys.argv[1]
    odir = sys.argv[2]

    base_dir   = os.path.join(odir,tag)
    output_dir = os.path.join("../dat/",tag)

    mk_dir(output_dir)

    # Define paths and constants
    obs_dir = '/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
    obs_list_file = '/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
    suffixs = {'SF': 'discharge', 'WL': 'level', 'RS': 'level'}

    # Load observation list
    ObsList = pd.read_csv(obs_list_file)
    Obs_NMs = ObsList['Obs_NM'].values
    obs_type_dict = dict(zip(ObsList['Obs_NM'], ObsList['ObsType']))

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
        SubId    = read_subid(obs_file)

        # Read SE_Hydrograph
        hydro_file = f"{base_dir}/{Obs_NM}_{bestTrail:02d}/best_Raven/output/SE_Hydrographs.csv"
        try:
            df_hyd = pd.read_csv(hydro_file)
        except Exception as e:
            print(f"\tFailed to read {hydro_file}: {e}")
            continue

        # Filter columns
        sub_cols = df_hyd.filter(regex=f"sub{SubId}").columns.tolist()
        if not sub_cols:
            print(f"\tsub{SubId} not found in {hydro_file}")
            continue

        if not df_list:
            cols = core_cols + sub_cols
        else:
            cols = ['date'] + sub_cols

        df_hyd = df_hyd.loc[:, cols]
        df_list.append(df_hyd)

        print(f"Processed: {Obs_NM} (Trail {bestTrail}, SubId {SubId})")

    # Merge all hydrographs on 'date'
    if not df_list:
        print("No hydrographs to merge.")
        sys.exit(0)

    df = df_list[0]
    for df_next in df_list[1:]:
        df = pd.merge(df, df_next, on='date', how='outer')

    mk_dir(output_dir)
    df.to_csv(f"{output_dir}/SE_Hydrographs.csv", index=False)
    print(f"Saved merged hydrographs to {output_dir}/SE_Hydrographs.csv")

#====================================================================================================
if __name__ == "__main__":
    main()