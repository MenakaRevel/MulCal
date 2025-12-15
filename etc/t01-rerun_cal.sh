#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --ntasks=20                               # number of MPI processes
#SBATCH --mem-per-cpu=10G                         # memory; default unit is megabytes
##SBATCH --mail-user=menaka.revel@uwaterloo.ca     # email address for notifications
#SBATCH --mail-type=ALL                           # email send only in case of failure
#SBATCH --time=0-2:00                              # time (DD-HH:MM)
#SBATCH --job-name=rerun-cal                        # jobname

# load pythons
module load python/3.12.4

# load module
module load scipy-stack

# cd into
cd $1

# remove processor
rm -rf processor_*

# link forcing
# ln -sf /home/menaka/projects/def-btolson/menaka/SW_OstrichRaven/RavenInput/forcing  ./RavenInput/forcing

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


echo "===================================================="
echo "===================================================="
echo "                 Remove Files                       "
echo "===================================================="
# Forcing and processor dirs
echo " Removing forcing and processor directories..."
# rm -rf ./RavenInput/forcing
rm -rf ./processor_*

# Ost txt files
echo " Removing Ostrich output text files..."
rm -rf ./OstErrors*.txt
rm -rf ./OstModel*.txt
rm -rf ./OstOutput*.txt

echo "===================================================="
echo "end: $(date)"
echo "===================================================="
wait
exit 0