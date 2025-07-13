#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=ALL                          # email send only in case of failure
#SBATCH --time=00-06:00  
#SBATCH --job-name=run-best-Raven

# load python
module load python/3.12.4

# load module
module load scipy-stack
#==================
echo "start: $(date)"
#==================
Obs_NM=$1
Num=`printf '%02g' "$2"`
ModelName="SE"
#==================
cd /home/menaka/scratch/MulCal/${Obs_NM}_${Num}
mkdir -p best_Raven
cd best_Raven
`pwd`
cp -r ../processor_0/best/RavenInput/* .
cp -r ../RavenInput/forcing .
cp -r ../RavenInput/obs .
cp -r ../RavenInput/SubBasinProperties.rvh .
#==================
# change rvi
rvi='SE.rvi'
tmp='tmp.rvi'
echo "update rvi: $rvi"
awk '
BEGIN {
    validation_period = "# Validation Period\n:EvaluationPeriod VALIDATION 2002-10-01 2008-09-30\n";
    calibration_period = "# Calibration Period\n:EvaluationPeriod CALIBRATION 2008-10-01 2018-09-30";
    start_date_pattern = ":StartDate[[:space:]]+2007-10-01";
    output_directives = ":WriteWaterLevels\n:WriteMassBalanceFile\n:WriteReservoirMBFile\n:EvaluationMetrics\t\tNASH_SUTCLIFFE    PCT_BIAS    KLING_GUPTA    KLING_GUPTA_DEVIATION   R2";
    found_metrics_section = 0;
    validation_inserted = 0;
}
{
    # Replace the StartDate
    if ($0 ~ start_date_pattern) {
        sub("2007-10-01", "2001-10-01", $0);
    }
    # Insert the validation period above the calibration period
    if ($0 ~ "# Calibration Period" && !validation_inserted) {
        print validation_period;
        validation_inserted = 1;
    }
    # Add output directives after the metrics section
    if ($0 ~ "# Defines the hydrograph performance metrics output by Raven." && !found_metrics_section) {
        found_metrics_section = 1;
        print $0;
        print ":WriteWaterLevels";
        print ":WriteMassBalanceFile";
        print ":WriteReservoirMBFile";
        print ":EvaluationMetrics\t\tNASH_SUTCLIFFE    PCT_BIAS    KLING_GUPTA    KLING_GUPTA_DEVIATION   R2  KGE_PRIME  PCT_PDIFF  SPEARMAN  PDIFF";
        next;
    }
    if (found_metrics_section && /^:/) next; # Skip original output directives
    print $0;
}
' "$rvi" > "$tmp"

# Replace original file with modified file
mv "$tmp" "$rvi"

# echo 'after rvi'
# cat $rvi
./Raven.exe SE -o ./output

wait
exit 0