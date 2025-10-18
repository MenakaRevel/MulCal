#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=FAIL                         # email send only in case of failure
#SBATCH --time=00-01:00  
#SBATCH --job-name=clean-all

# Usage: ./run_all_collect.sh LOCAL3
# Runs all the data collection scripts with the given tag

# if [ "$#" -ne 1 ]; then
#     echo "Usage: $0 <tag>"
#     exit 1
# fi

source $HOME/py312/bin/activate

reg=$1
tag=$2 #"Local-0" #
# odir="/home/menaka/scratch/MulCal/out"
odir="/home/menaka/scratch/MulCal/SE.out"

echo "Running all clean scripts for tag: $tag"  "$reg"

echo "Running remove_processor_dir.py..."
python remove_processor_dir.py "$reg" "$tag" "$odir" || { echo "Failed: remove_processor_dir.py"; exit 1; }

echo "Running remove_Ost_files.py..."
python remove_Ost_files.py "$reg" "$tag" "$odir" || { echo "Failed: remove_Ost_files.py"; exit 1; }

echo "Running softlink_forcing.py..."
python softlink_forcing.py "$reg" "$tag" "$odir" || { echo "Failed: softlink_forcing.py"; exit 1; }


echo "✅ All cleaned sucessfully for tag: $tag"