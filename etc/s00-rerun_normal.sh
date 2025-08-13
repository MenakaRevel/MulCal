#!/bin/bash

# Set paths
obs_file="../dat/GaugeSpecificList.csv"
outdir="/home/menaka/scratch/MulCal/out"    # out path
expName="Local-0"                           # experiment name

# Read Obs_NM values from CSV, skipping header
obs_list=$(tail -n +2 "$obs_file" | cut -d',' -f1)

echo "Checking for missing dds_status.out files..."

# Loop through each Obs_NM
for obs in $obs_list; do
    for n in $(seq -w 1 10); do
        status_path="${outdir}/${expName}/${obs}_${n}/dds_status.out"
        if [ ! -f "$status_path" ]; then
            # echo "  • Missing: $status_path"
            echo "${obs} ${n}"
            echo "t01-rerun_cal.sh ${outdir}/${expName}/${obs}_${n}"
            # sbatch t01-rerun_cal.sh "${outdir}/${expName}/${obs}_${n}"
        fi
    done
done
