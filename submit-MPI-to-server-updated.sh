#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --ntasks=20                               # number of MPI processes
#SBATCH --mem-per-cpu=10G                         # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca     # email address for notifications
#SBATCH --mail-type=ALL                           # email send only in case of failure
#SBATCH --time=0-48:00                            # time (DD-HH:MM)
#SBATCH --job-name=02KB001                       # jobname

# load pythons
module load python/3.12.4

# load module
module load scipy-stack
#==================
echo "start: $(date)"
#==================
Obs_NM="02KB001"
ModelName="SE"
# SubId=26007677
# ObsType="SF"
expname=$Obs_NM
MaxIter=5000
runname='Init' #'Restart' #
ObsDir='/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
#==================
if [[ "$runname" == 'Init' ]]; then
    rm -rf /home/menaka/scratch/MulCal/$expname
    mkdir -p /home/menaka/scratch/MulCal/$expname
    cd /home/menaka/scratch/MulCal/$expname
    pwd

    # copy OstrichRaven
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/OstrichRaven/* .

    mkdir ./RavenInput/obs

    # copy src files
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/src/* .

    # copy run_best_Raven.sh
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/run_best_Raven_MPI.sh .

    #========================
    # Init - intialization
    #========================
    echo create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList
    python create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList

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
    cd /home/menaka/scratch/MulCal/$expname
    pwd
    
    # add OstrichWarmStart yes to ostIn.txt
    sed -i '/#OstrichWarmStart      yes/c\OstrichWarmStart      yes' ostIn.txt

    # edit ModelSubdir in ostIn.txt
    sed -i '/ModelSubdir processor_/c\ModelSubdir processor_v2_' ostIn.txt

    # update  ostIn.txt
    sed -i "/MaxIterations/c\	MaxIterations         $MaxIterations" ostIn.txt
fi

# run parallel MPI
echo "srun ./OstrichMPI"
mpirun -np $SLURM_NTASKS ./OstrichMPI                # mpirun or mpiexec also work
# ./Ostrich

# run best Raven
echo "./run_best_Raven_MPI.sh"
./run_best_Raven_MPI.sh $expname

echo "end: $(date)"
wait
exit 0