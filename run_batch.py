#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_batch.py  --  Calibrate one gauge (Obs_NM) in a META‑Farm task.

This script is called by META‑Farm for every gauge listed in meta-farm.yaml.
It must finish successfully (exit 0) so downstream tasks can start.
"""

import argparse, logging, subprocess, sys, os
from pathlib import Path
import pandas as pd

# ------------------------------------------------------------------ #
# 0.  Configuration tables                                            #
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

GAUGE_CSV = Path("./dat/GaugeSpecificList.csv")
CW_CSV    = Path("./dat/LakeCWList.csv")

RAVEN_WRAPPER = Path("./submit-MPI-template.sh")   # your shell script

# ------------------------------------------------------------------ #
# 1.  CLI parsing                                                     #
# ------------------------------------------------------------------ #
ap = argparse.ArgumentParser()
ap.add_argument("Obs_NM",   help="Gauge code (e.g., 02MC028)")
ap.add_argument("--targetG", type=int, required=True,
                help="River sequence level (1=upstream)")
ap.add_argument("--expName", default="default",
                help="Experiment profile (Local-0 / Local-1 / Local-3)")
args = ap.parse_args()

if args.expName not in EXPERIMENTS:
    sys.exit(f"Unknown experiment '{args.expName}'")

cfg = EXPERIMENTS[args.expName]
tf  = lambda b: "True" if b else "False"   # bool -> string

# ------------------------------------------------------------------ #
# 2.  Logging                                                         #
# ------------------------------------------------------------------ #
LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)
logfile = LOG_DIR / f"{args.Obs_NM}.log"

logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(args.Obs_NM)
log.info("=== Starting calibration for %s ===", args.Obs_NM)
log.info("Config: %s", cfg)

# ------------------------------------------------------------------ #
# 3.  Run Raven/Ostrich via your shell wrapper                        #
# ------------------------------------------------------------------ #

# ------------------------------------------------------------------ #
# 3.  Patch and submit the job‑array script                          #
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

script = TEMPLATE.replace("{Obs_NM}", obs)
for tag, value in replacements.items():
    script = script.replace(tag, value)

OUTFILE.write_text(script)

cmd =[OUTFILE]
log.info("Running command: %s", " ".join(cmd))

'''
try:
    subprocess.check_call(cmd)
    log.info("Calibration finished OK")
except subprocess.CalledProcessError as e:
    log.error("Calibration failed (exit %s)", e.returncode)
    sys.exit(e.returncode)

# ------------------------------------------------------------------ #
# 4.  Update LakeCWList.csv for this level                     #
# ------------------------------------------------------------------ #
def update_lake_cw():
    """Write cal.CW for lakes this level."""
    ObsList = pd.read_csv(GAUGE_CSV)
    CWList  = pd.read_csv(CW_CSV)

    if args.targetG <= 1 or not cfg["calLakeCW"]:
        return

    rivseq_up = ObsList.query("rivseq == @args.targetG - 1")["Obs_NM"].values
    if args.Obs_NM not in rivseq_up:
        # This gauge isn't in upstream set; nothing to do.
        return

    # Read last line of dds_status.out produced by the wrapper
    status_file = Path(f"./{args.Obs_NM}_dds/dds_status.out")
    if not status_file.exists():
        log.warning("dds_status.out missing: %s", status_file)
        return

    df = pd.read_csv(status_file, sep=r"\s+")
    if cfg["CWindv"]:
        cw_val = df[f"w_{args.Obs_NM}"].iloc[-1]
    else:
        k_multi = df["k_multi"].iloc[-1]
        init_cw = CWList.loc[CWList["Obs_NM"] == args.Obs_NM, "ini.CW"].values[0]
        cw_val  = k_multi * init_cw

    CWList.loc[CWList["Obs_NM"] == args.Obs_NM, "cal.CW"] = cw_val
    CWList.to_csv(CW_CSV, index=False)
    log.info("Updated CW for %s -> %.3f", args.Obs_NM, cw_val)

update_lake_cw()

log.info("=== Completed %s ===", args.Obs_NM)
'''