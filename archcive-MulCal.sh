#!/bin/bash

# submit with:
#       sbatch archcive-MulCal.sh  


#!/bin/bash
#SBATCH --account=def-btolson
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=2G
#SBATCH --time=0-06:00
#SBATCH --job-name=archive-MulCal
#SBATCH --mail-user=menaka.revel@uwaterloo.ca
#SBATCH --mail-type=FAIL

tag='LOCAL2'
ZSTD=$HOME/zstd_install/bin/zstd

cd $SLURM_TMPDIR
cp -r /home/menaka/scratch/MulCal_${tag} .

tar -cf - MulCal_${tag} | $ZSTD -T${SLURM_CPUS_PER_TASK} -o MulCal_${tag}.tar.zst

cp MulCal_${tag}.tar.zst /home/menaka/nearline/def-btolson/menaka/


# # # #SBATCH --account=def-btolson
# # # #SBATCH --ntasks=1                                # number of MPI processes
# # # #SBATCH --mem-per-cpu=10G                          # memory; default unit is megabytes
# # # #SBATCH --mail-user=menaka.revel@uwaterloo.ca     # email address for notifications
# # # #SBATCH --mail-type=FAIL                          # email send only in case of failure
# # # #SBATCH --time=5-00:00                            # time (DD-HH:MM)
# # # #SBATCH --job-name=archive-MulCal                 # jobname

# # # tag='LOCAL3'

# # # tar -czf /home/menaka/scratch/MulCal_${tag}.tar.gz /home/menaka/scratch/MulCal_${tag} 

# # # mv /home/menaka/scratch/MulCal_${tag}.tar.gz  /home/menaka/nearline/def-btolson/menaka/MulCal_${tag}.tar.gz 

# # # wait