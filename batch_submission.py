#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launch Raven‐MPI jobs for a gauge group.

Usage
-----
python run_batch.py <targetG:int 1‑5> <expName>

expName ∈ {"Local-0", "Local-1", "default"}
"""

import os
import sys
import pandas as pd
from pathlib import Path
from collections import defaultdict

# ------------------------------------------------------------------ #
# 0.  Experiment presets (edit here only)                            #
# ------------------------------------------------------------------ #
EXPERIMENTS = {
    "Local-0": dict(BiasCorr=False, calSoil=False, calRivRoute=False,
                    calCatRoute=False, calLakeCW=False, CWindv=False),
    "Local-1": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=False),
    "Local-3": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=True),
    "default": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=True),
}

# ------------------------------------------------------------------ #
# 1.  CLI args                                                       #
# ------------------------------------------------------------------ #
try:
    targetG = int(sys.argv[1])               # 1‒5
    expName = sys.argv[2]
except (IndexError, ValueError):
    sys.exit("Usage: run_batch.py <targetG:int> <expName>")

if expName not in EXPERIMENTS:
    sys.exit(f"expName must be one of {', '.join(EXPERIMENTS)}")

cfg = EXPERIMENTS[expName]                   # dict of booleans
tf  = lambda b: "True" if b else "False"     # to string for template

print(f"► Gauge group   : {targetG}")
print(f"► Experiment    : {expName}")
print("► Switches      :", ", ".join(f"{k}={tf(v)}" for k, v in cfg.items()))

# ------------------------------------------------------------------ #
# 2.  Read data tables                                               #
# ------------------------------------------------------------------ #
ObsList = pd.read_csv("./dat/GaugeSpecificList.csv")
CWList  = pd.read_csv("./dat/LakeCWList.csv")

Obs_NMs = ObsList.query("rivseq == @targetG")["Obs_NM"].values

# ------------------------------------------------------------------ #
# 3.  Optional: compute lake CW values for upstream gauges           #
# ------------------------------------------------------------------ #
if targetG > 1 and cfg["calLakeCW"]:
    CW_values = {}
    rivseq_up = ObsList.query("rivseq == @targetG - 1")["Obs_NM"].values

    for up_groups in CWList["Obs_NM"].dropna():
        for lake in up_groups.split("&"):
            if lake not in rivseq_up:
                continue

            best_obj, best_paras = float("-inf"), None
            for n in range(1, 11):
                status = Path(f"/home/menaka/scratch/MulCal/{lake}_{n:02d}/dds_status.out")
                try:
                    df = pd.read_csv(status, sep=r"\s+")
                    obj = -df["OBJ._FUNCTION"].iloc[-1]
                    if obj > best_obj:
                        best_obj, best_paras = obj, df
                except Exception:
                    print("  • missing file:", status)

            if best_paras is None:
                continue

            if cfg["CWindv"]:
                CW_values[lake] = best_paras[f"w_{lake}"].iloc[-1]
            else:
                k_multi = best_paras["k_multi"].iloc[-1]
                init_cw = CWList.loc[CWList["Obs_NM"] == lake, "ini.CW"].values[0]
                CW_values[lake] = k_multi * init_cw

    if CW_values:
        CWList.loc[CWList["Obs_NM"].isin(CW_values), "cal.CW"] = \
            CWList["Obs_NM"].map(CW_values)
        CWList.to_csv("./dat/LakeCWList.csv", index=False)
        print("► Lake CW updated for", ", ".join(CW_values))

# ------------------------------------------------------------------ #
# 4.  Patch and submit the job‑array script                          #
# ------------------------------------------------------------------ #
TEMPLATE = Path("submit-MPI-to-server-batch_jobarray.sh").read_text()
OUTFILE  = Path("submit-MPI-to-server-updated_jobarray.sh")

replacements = {
    "{BiasCorr}"    : tf(cfg["BiasCorr"]),
    "{calSoil}"     : tf(cfg["calSoil"]),
    "{calRivRoute}" : tf(cfg["calRivRoute"]),
    "{calCatRoute}" : tf(cfg["calCatRoute"]),
    "{calLakeCW}"   : tf(cfg["calLakeCW"]),
    "{CWindv}"      : tf(cfg["CWindv"]),
}

for obs in Obs_NMs:
    script = TEMPLATE.replace("{Obs_NM}", obs)
    for tag, value in replacements.items():
        script = script.replace(tag, value)

    OUTFILE.write_text(script)
    print(f"  → sbatch {OUTFILE}  ({obs})")
    os.system(f"sbatch {OUTFILE}")
