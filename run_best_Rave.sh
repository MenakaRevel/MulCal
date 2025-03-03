#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=ALL                          # email send only in case of failure
#SBATCH --time=00-100:00  
#SBATCH --job-name=02KF013

# load python
module load python/3.12.4

# load module
module load scipy-stack
#==================
echo "start: $(date)"
#==================
Obs_NM="02KF013"
ModelName="SE"
#==================
cd /home/menaka/scratch/MulCal/$Obs_NM
mkdir -p best_Raven
cd best_Raven
`pwd`
cp -r ../processor_0/best/RavenInput/* .
cp -r ../RavenInput/forcing .
cp -r ../RavenInput/obs .
#==================
# change rvi
rvi='SE.rvi'
tmp='tmp.rvi'
# echo 'before rvi'
# cat $rvi
# Use awk to modify the required section
awk 'BEGIN {found=0} 
{
    if (/^# Defines the hydrograph performance metrics output by Raven\./) {
        found=1; print $0; 
        print ":WriteWaterLevels"; 
        print ":WriteMassBalanceFile"; 
        print ":WriteReservoirMBFile"; 
        print ":EvaluationMetrics\t\tNASH_SUTCLIFFE    PCT_BIAS    KLING_GUPTA    KLING_GUPTA_DEVIATION   R2";
        next;
    }
    if (found && /^:/) next; # Skip original output directives
    print $0;
}' "$rvi" > "$tmp"

# Replace original file with modified file
mv "$tmp" "$rvi"

# echo 'after rvi'
# cat $rvi
./Raven.exe SE -o ./output

wait
exit 0