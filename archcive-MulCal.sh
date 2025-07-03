#!/bin/bash

# submit with:
#       sbatch archcive-MulCal.sh  

#SBATCH --account=def-btolson
#SBATCH --ntasks=1                                # number of MPI processes
#SBATCH --mem-per-cpu=1G                          # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca     # email address for notifications
#SBATCH --mail-type=FAIL                          # email send only in case of failure
#SBATCH --time=0-48:00                            # time (DD-HH:MM)
#SBATCH --job-name=archive-MulCal                 # jobname

tag='LOCAL3'

tar -czvf /home/menaka/scratch/MulCal_{$tag}.tar.gz /home/menaka/scratch/MulCal 

mv /home/menaka/scratch/MulCal_{$tag}.tar.gz  /home/menaka/nearline/def-btolson/menaka/MulCal_{$tag}.tar.gz 

wait