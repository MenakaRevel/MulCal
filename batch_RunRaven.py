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
    "Local-0": dict(BiasCorr=True, calSoil=False, calRivRoute=False,
                    calCatRoute=False, calLakeCW=False, CWindv=False),
    "Local-1": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=False),
    "Local-2": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=True),
    "default": dict(BiasCorr=True,  calSoil=True,  calRivRoute=True,
                    calCatRoute=True,  calLakeCW=True,  CWindv=True),
}

# ------------------------------------------------------------------ #
# 1.  CLI args                                                       #
# ------------------------------------------------------------------ #
try:
    # targetG = int(sys.argv[1])               # 1‒5
    expName = sys.argv[1]
except (IndexError, ValueError):
    sys.exit("Usage: run_batch.py <expName>")

# if expName not in EXPERIMENTS:
#     sys.exit(f"expName must be one of {', '.join(EXPERIMENTS)}")

# cfg = EXPERIMENTS[expName]                   # dict of booleans
# tf  = lambda b: "True" if b else "False"     # to string for template

# print(f"► Gauge group   : {targetG}")
# print(f"► Experiment    : {expName}")
# print("► Switches      :", ", ".join(f"{k}={tf(v)}" for k, v in cfg.items()))

# ------------------------------------------------------------------ #
# 2.  Read data tables                                               #
# ------------------------------------------------------------------ #
ObsList = pd.read_csv("./dat/GaugeSpecificList.csv")
CWList  = pd.read_csv("./dat/LakeCWList.csv")

Obs_NMs = ObsList["Obs_NM"].values[1::]

for Obs_NM in Obs_NMs:
    # run best Raven
    print(f"sbatch run_best_Raven.sh {Obs_NM} {expName}")
    os.system(f"sbatch run_best_Raven.sh {Obs_NM} {expName}")