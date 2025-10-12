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
#SBATCH --job-name=UptLake-Burntroot #02KF013 #02KF016 #02KB001                    # jobname
### #SBATCH --begin=now+{delay}hour

# load pythons
module load python/3.12.4

# load module
module load scipy-stack
#==================
# Main Code
#==================
Obs_NM="Burntroot" #"02KF013" #"02KF016" #"02KB001"
ModelName="SE"
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
intag='Local-2'
tag='LakeUpdate'
#==================
# Calibration Options
BiasCorr='True' # 'False'
calSoil='True '  
calRivRoute='True' # 'True'
calCatRoute='True' # 'True'
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

# make new folder and step into it.
mkdir -p /home/menaka/scratch/MulCal/out/$tag/${expname}_${Num}
cd /home/menaka/scratch/MulCal/out/$tag/${expname}_${Num}

cp -rf /home/menaka/scratch/MulCal/out/$intag/${expname}_${Num}/* .

pwd

# remove processor
rm -rf processor_*

# copy new Lakes.rvh
cp -rf /home/menaka/projects/def-btolson/menaka/MulCal/OstrichRaven/RavenInput/Lakes.rvh.upd  ./RavenInput/Lakes.rvh

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