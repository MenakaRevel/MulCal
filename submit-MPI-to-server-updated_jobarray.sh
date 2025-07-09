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
#SBATCH --job-name=Animoosh                       # jobname
### #SBATCH --begin=now+{delay}hour

# load pythons
module load python/3.12.4

# load module
module load scipy-stack
#==================
# Main Code
#==================
Obs_NM="Animoosh"
ModelName="SE"
# SubId=26007677
# ObsType="SF"
expname="Animoosh" ##$Obs_NM
MaxIter=2000
runname='Init' #'Restart' #
ProgramType='ParallelDDS'
CostFunction='negKGE'
Num=`printf '%02g' "${SLURM_ARRAY_TASK_ID}"`
ObsDir='/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
CWindv=False  #'False' #'True'
BiasCorr=True # 'False'
calCatRoute=True # 'True'
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
echo "Individual CW Calibration         :"False
echo "Bias Correction                   :"True
echo "Calibrate Catchment Route         :"True
echo "===================================================="
#==================
if [[ "$runname" == 'Init' ]]; then
    rm -rf /home/menaka/scratch/MulCal/${expname}_${Num}
    mkdir -p /home/menaka/scratch/MulCal/${expname}_${Num}
    cd /home/menaka/scratch/MulCal/${expname}_${Num}
    pwd

    # copy OstrichRaven
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/OstrichRaven/* .

    # copy newest Raven excutable 
    cp -r /project/def-btolson/menaka/RavenHydroFramework/src/Raven.exe ./RavenInput/

    mkdir ./RavenInput/obs

    # copy src files
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/src/* .

    # copy run_best_Raven.sh
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/run_best_Raven_MPI.sh .

    #========================
    # Init - intialization
    #========================
    echo create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList $CWindv $BiasCorr $calCatRoute
    python create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList $CWindv $BiasCorr $calCatRoute

    #========================
    # rvt
    #========================
    echo update_rvt.py $Obs_NM $ObsDir "./RavenInput/SE.rvt" 
    python update_rvt.py $Obs_NM $ObsDir "./RavenInput/SE.rvt" 

    #========================
    # rvh
    #========================
    echo update_rvh_tpl.py $CWList        #$Obs_NM  "./SE.rvh.tpl"
    python update_rvh_tpl.py $CWList      #$Obs_NM "./SE.rvh.tpl"

    #========================
    # ostIn.txt
    #========================
    echo create_ostIn.py $SLURM_NTASKS $MaxIter #$RandomSeed 
    python create_ostIn.py $SLURM_NTASKS $MaxIter #$RandomSeed 
else
    cd /home/menaka/scratch/MulCal/${expname}_${Num}
    pwd
    
    # add OstrichWarmStart yes to ostIn.txt
    sed -i '/#OstrichWarmStart      yes/c\OstrichWarmStart      yes' ostIn.txt

    # edit ModelSubdir in ostIn.txt
    sed -i '/ModelSubdir processor_/c\ModelSubdir processor_v2_' ostIn.txt

    # update  ostIn.txt
    sed -i "/MaxIterations/c\	MaxIterations         $MaxIterations" ostIn.txt
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