#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import numpy as np
import pandas as pd
import os
import sys
import re
import random
import warnings
warnings.filterwarnings("ignore")
#================================================================
def read_cal_gagues(RavenDir, filename='SE.rvt'):
    # Define a regular expression pattern to match the desired lines
    pattern = r'^:RedirectToFile\s+\.\/obs\/(.*?)(?<!_weight)\.rvt'
    # pattern = r'^:RedirectToFile\s+\.\/obs\/(.*?)(?<!_weight)(?<!_discharge)(?<!_level)\.rvt'

    # Open the file and read its lines
    with open(RavenDir+"/"+filename, 'r') as file:
        lines = file.readlines()

    # Extract values matching the pattern starting from line 39
    values = {}
    # tags = 
    skip_lines = False
    for line in lines[30:]:
        # print (line)
        if '# Streamflow' in line:
            tag='SF'
        elif '# River Water Level' in line:
            tag='WL'
        elif '# Reservoir Stage' in line:
            tag='RS'
        #==========
        if 'weight' in line:
            skip_lines = True
            continue
        elif 'Weight' in line:
            skip_lines = True
            continue
        elif '#' in line:
            skip_lines = True
            continue
        elif '# Inflow' in line:
            skip_lines = True
            break
        
        # if skip_lines:
        #     break
        
        match = re.match(pattern, line)
        if match:
            values[match.group(1).split("_")[0]]=tag
            # values.append(match.group(1))
            # tags.append(tag)
    return values #, tags
#================================================================
def read_subid(fname):
    """Extracts the station ID from the ObservationData line, handling variable keywords."""
    with open(fname, 'r') as f:
        text=f.read()

    match = re.search(r'ObservationData\s+\S+\s+(\d+)', text)
    return int(match.group(1)) if match else 0
#================================================================
suffixs = {
    'SF':'discharge',
    'WL':'level',
    'RS':'level'
}
#================================================================
Obs_NM=sys.argv[1]
ModelName=sys.argv[2]
MaxIter=sys.argv[3]
ObsDir=sys.argv[4]
ObsList=sys.argv[5]
CWList=sys.argv[6]
BiasCorr=sys.argv[7]
calSoil=sys.argv[8]
calRivRoute=sys.argv[9]
calCatRoute=sys.argv[10]
calLakeCW=sys.argv[11]
CWindv=sys.argv[12]
#================================================================
# read GaugeSpecificList.csv
if ObsList == '':
    ObsList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/GaugeSpecificList.csv'
ObsList = pd.read_csv(ObsList)
# print (ObsList.head())
#================================================================
# read LakeCWList.csv
if CWList == '':
    CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
CWList = pd.read_csv(CWList)
#================================================================
# print (read_cal_gagues("./RavenInput"))
ObsType=ObsList[ObsList['Obs_NM']==Obs_NM]['ObsType'].values[0] #read_cal_gagues("./RavenInput")[Obs_NM]
Obsrvt=os.path.join(ObsDir,Obs_NM+'_'+suffixs[ObsType]+'.rvt')
SubId=read_subid(Obsrvt)
#================================================================
BasinType=ObsList[ObsList['Obs_NM']==Obs_NM]['Type'].values[0]
if BasinType == 'Upstream':
    UpObsNMList = 'None'
    UpObsTypes  = ['None']
    UpSubIds    = ['None']
else:
    # AllObsTypes=read_cal_gagues("./RavenInput")
    UpObsNMList = ObsList[ObsList['Obs_NM']==Obs_NM]['UpGauges'].values[0]
    UpObsTypes  = [ObsList[ObsList['Obs_NM']==gau]['ObsType'].values[0] for gau in UpObsNMList.split('&')]
    UpSubIds    = [read_subid(os.path.join(ObsDir,UpObs_NM+'_'+suffixs[ObsType]+'.rvt')) for UpObs_NM, ObsType in zip(UpObsNMList.split('&'),UpObsTypes)]
# print (UpObsNMList, UpObsTypes)
if ObsType == "RS":
    iniCW = CWList[CWList['Obs_NM']==Obs_NM]['ini.CW'].values[0]
elif ObsType == "SF" and SubId in CWList['SubBasinID'].values:
    iniCW = CWList[CWList['Obs_NM']==Obs_NM]['ini.CW'].values[0]
else:
    iniCW = -9999.0
#================================================================
with open('./params.py', 'w') as f:
    f.write('import os')
    f.write('\nimport sys')
    f.write('\n#======================================')
    f.write('\n# defines the parameters ')
    f.write('\n#======================================')
    f.write('\ndef ModelName():')
    f.write('\n\treturn\t"'+str(ModelName)+'"')
    f.write('\n#--------------------------------------')
    f.write('\ndef Obs_NM():')
    f.write('\n\treturn\t"'+str(Obs_NM)+'"')
    f.write('\n#--------------------------------------')
    f.write('\ndef SubId():')
    f.write('\n\treturn\t'+str(SubId))
    f.write('\n#--------------------------------------')
    f.write('\ndef ObsType():')
    f.write('\n\treturn\t"'+str(ObsType)+'"')
    f.write('\n#--------------------------------------')
    f.write('\ndef InitCW():')
    f.write('\n\treturn\t'+str(iniCW))
    f.write('\n#--------------------------------------')
    f.write('\ndef BasinType():')
    f.write('\n\treturn\t"'+str(BasinType)+'"')
    f.write('\n#--------------------------------------')
    f.write('\ndef UpObsNMList():')
    f.write('\n\treturn\t['+','.join(f'"{g}"' for g in UpObsNMList.split('&'))+']')
    f.write('\n#--------------------------------------')
    f.write('\ndef UpObsTypes():')
    f.write('\n\treturn\t['+','.join(f'"{g}"' for g in UpObsTypes)+']')
    f.write('\n#--------------------------------------')
    f.write('\ndef UpSubIds():')
    f.write('\n\treturn\t['+','.join(f'{g}' for g in UpSubIds)+']')
    f.write('\n#--------------------------------------')
    f.write('\ndef MaxIter():')
    f.write('\n\treturn\t'+str(MaxIter))
    f.write('\n#--------------------------------------')
    f.write('\ndef calLakeCW():')
    f.write('\n\treturn\t'+str(calLakeCW))
    f.write('\n#--------------------------------------')
    f.write('\ndef CWindv():')
    f.write('\n\treturn\t'+str(CWindv))
    f.write('\n#--------------------------------------')
    f.write('\ndef BiasCorrection():')
    f.write('\n\treturn\t'+str(BiasCorr))
    f.write('\n#--------------------------------------')
    f.write('\ndef calSoil():')
    f.write('\n\treturn\t'+str(calSoil))
    f.write('\n#--------------------------------------')
    f.write('\ndef calCatRoute():')
    f.write('\n\treturn\t'+str(calCatRoute))
    f.write('\n#--------------------------------------')
    f.write('\ndef calRivRoute():')
    f.write('\n\treturn\t'+str(calRivRoute))
    f.write('\n#--------------------------------------')    