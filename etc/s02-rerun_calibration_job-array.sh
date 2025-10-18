#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --ntasks=20                               # number of MPI processes
#SBATCH --mem-per-cpu=10G                         # memory; default unit is megabytes
##SBATCH --mail-user=menaka.revel@uwaterloo.ca     # email address for notifications
#SBATCH --mail-type=ALL                           # email send only in case of failure
#SBATCH --array=1-10                              # submit as a job array 
#SBATCH --time=0-6:00                            # time (DD-HH:MM)
#SBATCH --job-name=rerun-02KB001                    # jobname
### #SBATCH --begin=now+{delay}hour

# load pythons
module load python/3.12.4

# load module
module load scipy-stack
#==================
# Main Code
#==================
Obs_NM="02KB001"           # get this from "outliler_lakes.csv" and "outliler_lakes_dryout.csv"
OutlierLakes="26007397"    # get this from "outliler_lakes.csv" and "outliler_lakes_dryout.csv" comma seperated list
ModelName="SW" # "SW" or "SF"
# SubId=26007677
# ObsType="SF"
expname=$Obs_NM  #"02KF013" ##$Obs_NM
MaxIter=2000
runname='Init' #'Restart' #
ProgramType='ParallelDDS'
CostFunction='negKGE'
Num=`printf '%02g' "${SLURM_ARRAY_TASK_ID}"`
ObsDir='/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
#==================
tag='Local-0f'
#==================
# Calibration Options
BiasCorr='False' # 'False'
calSoil='False '  
calRivRoute='False' # 'True'
calCatRoute='False' # 'True'
calLakeCW='True' # True
CWindv='True'  #'False' #'True'
#==================
# cd into main folder
`cd ..`
#==================
echo "===================================================="
echo "start: $(date)"
echo "===================================================="
echo ""
echo "Job Array ID / Job ID: $SLURM_ARRAY_JOB_ID / $SLURM_JOB_ID"
echo "This is job $SLURM_ARRAY_TASK_ID out of $SLURM_ARRAY_TASK_COUNT jobs."
echo ""
echo "===================================================="
echo "Experiment name: ${expname}_${Num} with $MaxIter calibration budget"
echo "===================================================="
echo "Experimental Settings"
echo "Experiment Name                   :"${expname}_${Num}
echo "Run Type                          :"${runname}
echo "Maximum Iterations                :"${MaxIter}
echo "Calibration Method                :"${ProgramType}
echo "Cost Function                     :"${CostFunction}
echo "Bias Correction                   :"True
echo "Calibrate Soil Parameters         :"True
echo "Calibrate River Route             :"True
echo "Calibrate Catchment Route         :"True
echo "Calibrate Lake Crest Widths       :"True
echo "Individual CW Calibration         :"True
echo "===================================================="
#==================
# if [[ "$runname" == 'Init' ]]; then
# rm -rf /home/menaka/scratch/MulCal/out/$tag/${expname}_${Num}
# mkdir -p /home/menaka/scratch/MulCal/out/$tag/${expname}_${Num}
cd /home/menaka/scratch/MulCal/out/$tag/${expname}_${Num}

# # cp all 1st iteration - backup
# mkdir -p calTrail-0
# cp -r * calTrail-0/ 

pwd

# remove processor
rm -rf processor_*

# Step 1: Modify ostIn.txt if the current lake is an outlier
# ----------------------------------------------------------
# Check if pm.SubId() from params.py is in the OutlierLakes list.
# If it is, comment out the line in ostIn.txt that starts with "w_${OBS_NM}".

# Step 2: Update reservoir crest width in rvh.tpl
# -----------------------------------------------
# Locate the line with ":SBGroupPropertyOverride     Lake_${OBS_NM}     RESERVOIR_CREST_WIDTH"
# and replace the existing value with 9999.0 to override the crest width for this lake.

OSubID=$(python3 -c "import params as pm; outliers = [int(x) for x in '''$OutlierLakes'''.split(',')]; print(pm.SubId()) if pm.SubId() in outliers else None")

echo $OSubID

if [ -n "$OSubID" ]; then
    echo "Individual lake CW calibred: $OSubID"
    echo "Editing ostIn.txt"

    # Comment out lines starting with 'w_${Obs_NM}'
    sed -i.bak "/^w_${Obs_NM}\b/ s/^/#/" ostIn.txt

    # Replace the RESERVOIR_CREST_WIDTH value with 9999.0 for Lake_${OBS_NM}
    sed -i "/^:SBGroupPropertyOverride[[:space:]]\+Lake_${Obs_NM}[[:space:]]\+RESERVOIR_CREST_WIDTH[[:space:]]\+[^\ ]\+/ s/[^ ]\+$/9999.0/" SE.rvh.tpl

    tail -2 SE.rvh.tpl
    echo ""
else
    echo "No individual lake CW calibred."
    echo "No need to edit ostIn.txt"
fi

# Remove the handled SubID from the list
GroupSubIDs=$(echo $OutlierLakes | tr ',' '\n' | grep -v "^$OSubID\$" | paste -sd' ' -)

# Only add to SE.rvh.tpl if there are remaining subids
if [ -n "$GroupSubIDs" ]; then
    cat <<EOF >> SE.rvh.tpl

:SubBasinGroup   OutlierLakes
    $GroupSubIDs
:EndSubBasinGroup
:SBGroupPropertyOverride     OutlierLakes          RESERVOIR_CREST_WIDTH  9999.0
EOF

    echo "Appended OutlierLakes group and crest width override to SE.rvh.tpl"
else
    echo "No additional subbasins to group. Nothing added to SE.rvh.tpl"
fi

echo "===================================================="
echo "===================================================="
echo "                     Ostrich                        "
echo "===================================================="
# run parallel MPI
echo "srun ./OstrichMPI"
mpirun -np $SLURM_NTASKS ./OstrichMPI                # mpirun or mpiexec also work
# ./Ostrich
echo "===================================================="
echo "===================================================="
echo "                      Raven                         "
echo "===================================================="
# run best Raven
echo "./run_best_Raven_MPI.sh"
./run_best_Raven_MPI.sh ${expname} ${Num}

# # remove the forcing - softlink
# python /home/menaka/projects/def-btolson/menaka/MulCal/etc/softlink_forcing.py
echo "===================================================="
echo "end: $(date)"
echo "===================================================="
wait
exit 0