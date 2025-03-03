#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
make :ReservoirTargetStage using anomaly --> remove mean
'''
import numpy as np
import pandas as pd
import os
import sys
import re
import warnings
warnings.filterwarnings("ignore")
#==================================
# Read the file
inputfile='/home/menaka/scratch/MulCal/02MC036/simRaven/obs/02MC037_level.rvt'
with open(inputfile, "r") as file:
    lines = file.readlines()


# Extract numeric data
values = []
for line in lines:
    try:
        value = float(line.strip())
        values.append(value)
    except ValueError:
        continue  # Ignore non-numeric lines

# Extract header dynamically
header = []
for i, line in enumerate(lines):
    header.append(line)
    if line.startswith(":ReservoirTargetStage"):
        header.append(lines[i + 1])  # Include the next line as well
        break

# Extract footer
footer_index = next(i for i, line in enumerate(lines) if line.strip() == ":EndObservationData")
footer = lines[footer_index:]

# Convert to numpy array
values = np.array(values)

# Filter out missing data (-1.2345)
valid_values = values[values != -1.2345]

# Compute mean
mean_value = np.mean(valid_values)

# Subtract mean from all valid values
adjusted_values = np.where(values != -1.2345, values - mean_value, values)

# Save adjusted data
ouputfile='/home/menaka/scratch/MulCal/02MC036/simRaven/obs/02MC037_level_ana.rvt'
with open(ouputfile, "w") as file:
    file.writelines(header)
    for value in adjusted_values:
        file.write(f"\t{value:.4f}\n")
    file.writelines(footer)

print(f"Mean value: {mean_value:.4f}")
print("Adjusted data saved to adjusted_data.txt")