#!/usr/bin/env python3
# make_meta_farm_yaml.py
"""
Create a meta‑farm YAML (meta-farm.yaml) from GaugeSpecificList.csv.

• One task per Obs_NM (gauge)
• Dependencies come from UpGauges (colon‐ or &: separated)
• Resources and walltime can be tweaked in the DEFAULTS dict
"""

import pandas as pd
from pathlib import Path
import yaml
import argparse

CSV = Path("dat/GaugeSpecificList.csv")   # source file
YAML_OUT = Path("meta-farm.yaml")         # output

DEFAULTS = dict(
    walltime="02:00:00",   # hh:mm:ss
    mem="10G",
    cpus=20,
    modules=["python/3.10"],
)

def parse_args():
    ap = argparse.ArgumentParser(description="Generate meta-farm.yaml")
    ap.add_argument("--exp", default="Local-1",
                    help="experiment name passed to run_batch.py")
    ap.add_argument("--wall", default=DEFAULTS["walltime"])
    ap.add_argument("--mem",  default=DEFAULTS["mem"])
    ap.add_argument("--cpus", default=DEFAULTS["cpus"], type=int)
    return ap.parse_args()

def up_to_list(up):
    """ 'a&b:c' -> ['a','b','c'] ; '', NaN -> [] """
    if pd.isna(up) or str(up).strip() == "":
        return []
    return [x.strip() for x in re.split(r"[:&]", str(up)) if x.strip()]

def main():
    args = parse_args()
    df = pd.read_csv(CSV)

    tasks = {}
    for _, row in df.iterrows():
        g        = row["Obs_NM"].strip()
        deps     = up_to_list(row["UpGauges"])
        rivseq   = int(row["rivseq"])

        cmd = (f"python run_batch.py {g} --targetG {rivseq} "
               f"--expName {args.exp}")

        tasks[g] = dict(
            cmd   = cmd,
            deps  = deps if deps else None,  # omit key if empty
            walltime = args.wall,
            mem      = args.mem,
            cpus     = args.cpus,
        )

    meta = dict(
        global_defaults = DEFAULTS,
        tasks = tasks
    )

    YAML_OUT.write_text(yaml.safe_dump(meta, sort_keys=False))
    print(f"✓ Wrote {YAML_OUT} with {len(tasks)} tasks.")

if __name__ == "__main__":
    import re
    main()
