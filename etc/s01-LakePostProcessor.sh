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

tag="Local-2" #"$1"
thrAmp=2.0 #m
odir="/home/menaka/scratch/MulCal/out"

python post-processing_lake.py ${tag} ${thrAmp} ${odir}