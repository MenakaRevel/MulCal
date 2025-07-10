#!/bin/bash

# Usage: ./run_all_collect.sh LOCAL3
# Runs all the data collection scripts with the given tag

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <tag>"
    exit 1
fi

tag="$1"

echo "Running all collect scripts for tag: $tag"

echo "Running remove_processor_dir.py..."
python remove_processor_dir.py "$tag" || { echo "Failed: remove_processor_dir.py"; exit 1; }

echo "Running softlink_forcing.py..."
python softlink_forcing.py "$tag" || { echo "Failed: softlink_forcing.py"; exit 1; }

echo "Running collect_all_para.py..."
python collect_all_para.py "$tag" || { echo "Failed: collect_all_para.py"; exit 1; }

echo "Running collect_hydrograph.py..."
python collect_hydrograph.py "$tag" || { echo "Failed: collect_hydrograph.py"; exit 1; }

echo "Running collect_resStages.py..."
python collect_resStages.py "$tag" || { echo "Failed: collect_resStages.py"; exit 1; }

echo "Running collect_siteCal.py..."
python collect_siteCal.py "$tag" || { echo "Failed: collect_siteCal.py"; exit 1; }

echo "✅ All scripts completed successfully for tag: $tag"
