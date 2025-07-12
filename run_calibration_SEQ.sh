#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
##SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=ALL                          # email send only in case of failure
#SBATCH --time=00-100:00  
#SBATCH --job-name=Animoosh

# load python
module load python/3.12.4

# load module
module load scipy-stack
#==================
echo "start: $(date)"
#==================
Obs_NM="NorthDepot" #"02KA015" #calMPI1_02KC015
ModelName="SE"
# SubId=26007677
# ObsType="SF"
expname=$Obs_NM
MaxIter=2
runname='Init' #'Restart' #
ObsDir='/home/menaka/projects/def-btolson/menaka/SEregion/OstrichRaven/RavenInput/obs'
ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
#==================
# Calibration Options
BiasCorr='True' # 'False'
calSoil='True'   
calRivRoute='True' # 'True'
calCatRoute='True' # 'True'
calLakeCW='True' # True
CWindv='True'  #'False' #'True'
#==================
if [[ "$runname" == 'Init' ]]; then
    mkdir -p /home/menaka/scratch/MulCal/${expname}_01
    cd /home/menaka/scratch/MulCal/${expname}_01
    pwd

    # copy OstrichRaven
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/OstrichRaven/* .

    mkdir -p ./RavenInput/obs

    # copy src files
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/src/* .

    # copy run_best_Raven.sh
    cp -r /home/menaka/projects/def-btolson/menaka/MulCal/run_best_Raven.sh .

    #========================
    # Init - logger
    #========================
    echo logger.py ${expname}_01
    python logger.py ${expname}_01

    #========================
    # Init - intialization
    #========================
    echo create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList  $BiasCorr $calSoil $calRivRoute $calCatRoute $calLakeCW $CWindv
    python create_params.py $Obs_NM $ModelName $MaxIter $ObsDir $ObsList $CWList $BiasCorr $calSoil $calRivRoute $calCatRoute $calLakeCW $CWindv

    #========================
    # rvt
    #========================
    echo update_rvt.py $Obs_NM $ObsDir "./RavenInput/SE.rvt" 
    python update_rvt.py $Obs_NM $ObsDir "./RavenInput/SE.rvt" 

    #========================
    # rvh
    #========================
    echo update_rvh.py $CWList        # $Obs_NM  "./SE.rvh.tpl" 
    python update_rvh_tpl.py $CWList  # $Obs_NM "./SE.rvh.tpl" 

    #========================
    # rvp
    #========================
    echo convert_rvp_tpl.py 
    python convert_rvp_tpl.py

    #========================
    # ostIn.txt
    #========================
    echo create_ostIn.py 0 $MaxIter #$RandomSeed 
    python create_ostIn.py 0 $MaxIter #$RandomSeed 
else
    cd /home/menaka/scratch/MulCal/$expname
    pwd
    
    # add OstrichWarmStart yes to ostIn.txt
    sed -i '/#OstrichWarmStart      yes/c\OstrichWarmStart      yes' ostIn.txt

    # update  ostIn.txt
    sed -i "/MaxIterations/c\	MaxIterations         $MaxIter" ostIn.txt
fi

# run parallel MPI
echo "./Ostrich"
./Ostrich

# # run best Raven
# echo "./run_best_Raven.sh"
# ./run_best_Raven.sh ${expname} '01'

echo "end: $(date)"
wait
exit 0