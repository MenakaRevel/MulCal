#! /usr/bin/python
#! utf+8
'''
convert_rvp_tpl.py: convert the rvp.tpl file to constant rvp 
'''
import pandas as pd 
import numpy as np 
import os
import sys
from logger import log
import params as pm
#================================================================
if not pm.calSoil():
    log.info("Soil parameters will not be calibrated .")
    rvp_tpl='./'+pm.ModelName()+'.rvp.tpl'
    with open(rvp_tpl, "r") as f:
        content = f.read()
    
    # Replace placeholders
    updated_content = content.replace("%MAX_BASEFLOW_RATE%", "10.0").replace("%BASEFLOW_N%", "2.0")

    # Save to file
    rvp_path = './'+pm.ModelName()+'.rvp'
    with open(rvp_path, "w") as f:
        f.write(updated_content)
else:
    log.info("Soil parameters will be calibrated .")