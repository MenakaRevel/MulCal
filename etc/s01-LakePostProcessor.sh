#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=FAIL                         # email send only in case of failure
#SBATCH --time=00-01:00  
#SBATCH --job-name=LakePostProcessor

# Usage: ./s02-LkePostProcessor.sh

# source $HOME/py312/bin/activate

tag="Local-0" #"$1"
thrAmp=5.0 #m
thrDry=0 # days
odir="/home/menaka/scratch/MulCal/out"

# lake amplitude
python check_lake_amplitude.py ${tag} ${thrAmp} ${odir}

# lake dry out
python check_lake_dryout.py ${tag} ${thrDry} ${odir}