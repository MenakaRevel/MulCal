#!/bin/bash

reg=$1     # region name
expName=$2 # "Local-2"                           # experiment name
rivseq=$3  # river segment sequence number

# Set paths
obs_file="../dat/"${reg}"/GaugeSpecificList.csv"
outdir="/home/menaka/scratch/MulCal/out"    # out path

# Read Obs_NM values from CSV, skipping header
# obs_list=$(tail -n +2 "$obs_file" | cut -d',' -f1)

# obs_list=$(awk -F',' 'NR>1 && $6=='${rivseq}' {print $1}' "$obs_file")
obs_list=$(awk -F',' -v r="$rivseq" 'NR>1 && $6==r {print $1}' "$obs_file")

echo $obs_list

echo "Checking for missing dds_status.out files in "${expName}" ..."

# Loop through each Obs_NM
for obs in $obs_list; do
    for n in $(seq -w 1 10); do
        status_path="${outdir}/${expName}/${obs}_${n}/dds_status.out"
        diagnose_path="${outdir}/${expName}/${obs}_${n}/best_Raven/output/${reg}_Diagnostics.csv" 
        if [[ ! -s "$status_path" || "$(wc -l < "$status_path")" -lt 2 ]]; then
            # echo "  • Missing: $status_path"
            echo "${obs} ${n}"
            echo "t01-rerun_cal.sh ${outdir}/${expName}/${obs}_${n}"
            sbatch t01-rerun_cal.sh "${outdir}/${expName}/${obs}_${n}"
        elif [[ ! -s "$diagnose_path" || "$(wc -l < "$diagnose_path")" -lt 2 ]]; then
            echo "${obs} ${n}"
            echo "t01-rerun_cal.sh ${outdir}/${expName}/${obs}_${n}"
            sbatch t01-rerun_cal.sh "${outdir}/${expName}/${obs}_${n}"
        fi
    done
done
