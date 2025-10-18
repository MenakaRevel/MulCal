#!/bin/bash

# submit with:
#       sbatch submit-MPI-to-server.sh  

#SBATCH --account=def-btolson
#SBATCH --mem-per-cpu=10G                        # memory; default unit is megabytes
#SBATCH --mail-user=menaka.revel@uwaterloo.ca    # email address for notifications
#SBATCH --mail-type=FAIL                         # email send only in case of failure
#SBATCH --time=00-01:00  
#SBATCH --job-name=collect-all

# Usage: ./run_all_collect.sh LOCAL3
# Runs all the data collection scripts with the given tag

# if [ "$#" -ne 1 ]; then
#     echo "Usage: $0 <tag>"
#     exit 1
# fi

source $HOME/py312/bin/activate
reg="$1"
tag="$2" #"Local-2" #"$1"
odir="/home/menaka/scratch/MulCal/out"

echo "Running all collect scripts for tag: $tag"

echo "Running collect_all_para.py..."
python collect_all_para.py "$reg" "$tag" "$odir" || { echo "Failed: collect_all_para.py"; exit 1; }

echo "Running collect_hydrograph.py..."
python collect_hydrograph.py "$reg" "$tag" "$odir" || { echo "Failed: collect_hydrograph.py"; exit 1; }

echo "Running collect_resStages.py..."
python collect_resStages.py "$reg" "$tag" "$odir" || { echo "Failed: collect_resStages.py"; exit 1; }

echo "Running collect_waterlevel.py..."
python collect_waterlevel.py "$reg" "$tag" "$odir" || { echo "Failed: collect_waterlevel.py"; exit 1; }

echo "Running collect_siteCal.py..."
python collect_siteCal.py "$reg" "$tag" "$odir" || { echo "Failed: collect_siteCal.py"; exit 1; }

echo "Running remove_processor_dir.py..."
python remove_processor_dir.py "$reg" "$tag" "$odir" || { echo "Failed: remove_processor_dir.py"; exit 1; }

echo "Running softlink_forcing.py..."
python softlink_forcing.py "$reg" "$tag" "$odir" || { echo "Failed: softlink_forcing.py"; exit 1; }

echo "✅ All scripts completed successfully for tag: $tag"
