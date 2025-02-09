#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import numpy as np
import pandas as pd
import os
import sys
import re
import warnings
warnings.filterwarnings("ignore")

import params as pm
#=================================================================================================
# Functions
#=================================================================================================
def Generate_Raven_rvt_String(varList, fileName):
    '''
    """Generate Raven input forcing file 

    Function that used to generate content of Raven input file.

    Parameters
    ----------
    varList           : list
    fileName          : data-type
    '''
    output_string_list = []
    output_string_list.append("#----------------------------------------------")
    output_string_list.append("# Raven Input file")
    output_string_list.append("# by BasinMaker Vxx")
    output_string_list.append("#----------------------------------------------")
    for i in range(0, len(varList)):
        if varList[i] == "runoff" or varList[i] == "RUNOFF":
            gridded_forcing_string      = "RUNOFF"
            gridded_forcing_type_string = "PRECIP"
            var_name_string             = "runoff"
        elif varList[i] == "Averagetemp" or varList[i] == "TEMP_AVE":
            gridded_forcing_string      = "Averagetemp"
            gridded_forcing_type_string = "TEMP_AVE"
            var_name_string             = "recharge"
        else:
            gridded_forcing_string      = varList[i].upper()
            gridded_forcing_type_string = varList[i].upper()
            var_name_string             = varList[i].lower()
        #====
        output_string_list.append(":GriddedForcing           "+gridded_forcing_string)
        output_string_list.append("    :ForcingType          "+gridded_forcing_type_string)
        output_string_list.append("    :FileNameNC           "+fileName[i])
        output_string_list.append("    :VarNameNC            "+var_name_string)
        output_string_list.append("    :DimNamesNC           rlon rlat time      # must be in the order of (x,y,t)")
        output_string_list.append("    :LinearTransform      24.0     0.0        # unit conversion")
        output_string_list.append("    :RedirectToFile       ./forcing/GriddedForcings.txt")                  
        output_string_list.append(":EndGriddedForcing")
        output_string_list.append(" ")
    output_string = "\n".join(output_string_list)
    return output_string
#=================================================================================================
def WriteStringToFile(Out_String, File_Path, WriteMethod):
    """Write String to a file

    Function that used to write Out_String to a file located at the File_Path.

    Parameters
    ----------
    Out_String            : string
        The string that will be writed to the file located at File_Path
    File_Path             : string
        Path and filename of file that will be modified or created
    WriteMethod           : {'a','w'}
        If WriteMethod = "w", a new file will be created at the File_Path
        If WriteMethod = "a", the Out_String will be added to exist file

    Notes
    ------
        The file located at the File_Path will be modified or created

    Returns
    -------
        None

    Examples
    --------
    >>> from WriteRavenInputs import WriteStringToFile
    >>> Out_String = 'sometest at line 1\n some test at line 2\n some test at line 3\n'
    >>> File_Path  = 'C:/Path_to_the_Flie_with_file_name'
    >>> WriteStringToFile(Out_String = Out_String,File_Path = File_Path,WriteMethod = 'w')

    """

    if os.path.exists(
        File_Path
    ):  ### if file exist, we can either modify or overwrite it
        with open(File_Path, WriteMethod) as f:
            f.write(Out_String)
    else:  ## create a new file anyway, since file did not exist
        with open(File_Path, "w") as f:
            f.write(Out_String)
#===============================================================================================
def Generate_Raven_Timeseries_rvt_String(obsnm, suffix="discharge"):  
    # Modify_template_rvt(obsnm):

    """Generate a string in Raven time series rvt input file format

    Function that used to modify raven model timeseries rvt file (Model_Name.rvt)
    Add  ":RedirectToFile    ./obs/{guagename}_{variable}.rvt"
    for each gauge in the end of model rvt file (Model_Name.rvt)

    Parameters
    ----------
    # # # outFolderraven            : String
    # # #     Path and name of the output folder of Raven input files
    # # # outObsfileFolder          : String
    # # #     Path and name of the output folder to save obervation rvt file
    # # #     of each gauge
    obsnm                     : data-type
        Dataframe of observation gauge information for this gauge including
        at least following two columns
        'Obs_NM': the name of the stream flow obsrvation gauge
        'SubId' : the subbasin Id of this stremflow gauge located at.
    # # Model_Name                : string
    # #     The Raven model base name. File name of the raven input will be
    # #     Model_Name.xxx.

    Notes
    ------
    None

    See Also
    --------
    DownloadStreamflowdata_US            : Generate flowdata inputs
                                           needed by this function
    DownloadStreamflowdata_CA            : Generate flowdata inputs
                                           needed by this function

    Returns
    -------
    output_string     : string
        It is the string that contains the content that will be used to
        modify the raven time series rvt input file of this gauge
    Examples
    --------
    >>> from WriteRavenInputs import Generate_Raven_Timeseries_rvt_String
    >>> outFolderraven    = 'c:/path_to_the_raven_input_folder/'
    >>> outObsfileFolder  = 'c:/path_to_the_raven_streamflow_observation gauge_folder/'
    >>> Subbasin_ID = 1
    >>> Station_NM  = '05127000'
    >>> obsnms = pd.DataFrame(data=[Subbasin_ID,Station_NM],columns=['SubId','Obs_NM'])
    >>> Model_Name = 'test'
    >>> output_string = Generate_Raven_Timeseries_rvt_String(outFolderraven,outObsfileFolder,obsnm,Model_Name)

    """

    # toobsrvtfile = os.path.join(outFolderraven, Model_Name + ".rvt")
    # obsflodername = "./" + os.path.split(outObsfileFolder)[1] + "/"
    output_string = (
        "  \n"
        + ":RedirectToFile    "
        + "./obs/"
        + obsnm
        + "_"
        + suffix
        + ".rvt"
        # + "  \n"
    )
    return output_string
#=================================================================================================
def replace_SubID_save(obs_rvt_file_path, Replace1, Replace2, out_rvt_file_path):
    # Open the rvt file in read mode
    with open(obs_rvt_file_path, 'r') as file:
        # Read the content of the file
        content = file.read()

    # Replace the __SubId__ placeholder with the actual subbasin ID
    # subbasin_id = 'your_subbasin_id'
    content = re.sub(Replace1, Replace2, content)

    # Open the rvt file in write mode to save the modified content
    with open(out_rvt_file_path, 'w') as file:
        file.write(content)

    return 0
#=================================================================================================
suffixs={
    'SF':'discharge',
    'WL':'level',
    'RS':'level'
}
#=================================================================================================
Obs_NM=sys.argv[1] # provided as a input
ObsDir=sys.argv[2]
GauType=pm.ObsType() # SF | WL | RS # provided as a input
# Create dictionary with values as keys and list of keys as values
UpObsDict = {}
for k, v in zip(pm.UpObsTypes(), pm.UpObsNMList()):
    UpObsDict.setdefault(k, []).append(v)
# print (UpObsDict)
upSF=UpObsDict.get("SF") or []
upRS=UpObsDict.get("RS") or []
# print (upSF, upRS)
#=================================================================================================
# create forcing rvt
RavenFolder="./RavenInput"

Model_rvt_string=Generate_Raven_rvt_String(varList = ['runoff','recharge','Averagetemp'],
fileName=[
    './forcing/GEM-HYDRO_aggregated_runoff.nc',
    './forcing/GEM-HYDRO_aggregated_recharge.nc',
    './forcing/GEM-HYDRO_aggregated_recharge.nc',
])

Model_rvt_file_path = os.path.join(RavenFolder, "SE.rvt")

WriteStringToFile(
    Model_rvt_string+'\n \n',Model_rvt_file_path,"w")

WriteStringToFile(
    '# Observation\n \n',Model_rvt_file_path,"a")

if GauType == 'SF':
    WriteStringToFile(
        '# Streamflow\n \n',Model_rvt_file_path,"a")
elif GauType == 'WL':
    WriteStringToFile(
        '# River Water Level\n \n',Model_rvt_file_path,"a")
elif GauType == 'RS':
    WriteStringToFile(
        '# Reservoir Stage\n \n',Model_rvt_file_path,"a")
#=============================================
# observation data
obs_rvt_file_path = (
    "\n"
    + ":RedirectToFile    "
    + "./obs/"
    + Obs_NM
    + "_"
    + suffixs[GauType]
    + ".rvt"
)

WriteStringToFile(
    obs_rvt_file_path+'\n \n',Model_rvt_file_path,"a")
#=============================================
# copy the file
os.system(
    'cp -r '+ObsDir+'/'+Obs_NM+'_'+suffixs[GauType]+'.rvt '+
    './RavenInput/obs/'+Obs_NM+'_'+suffixs[GauType]+'.rvt'
)
#=============================================
# observation weight
wgt_rvt_file_path = (
    "\n"
    + "#:RedirectToFile    "
    + "./obs/"
    + Obs_NM
    + "_"
    + suffixs[GauType]
    + "_"
    + "weight"
    + ".rvt"
)

WriteStringToFile(
    wgt_rvt_file_path+'\n \n',Model_rvt_file_path,"a")
#=============================================
# copy the file
os.system(
    'cp -r '+ObsDir+'/'+Obs_NM+'_'+suffixs[GauType]+'_weight.rvt '+
    './RavenInput/obs/'+Obs_NM+'_'+suffixs[GauType]+'_weight.rvt'
)
#=============================================
# Input data dicharge/lake water level
if len(upSF) > 0:
    print ("upSF")
    WriteStringToFile(
    '# Inflow - BasinInflowHydrograph\n \n',Model_rvt_file_path,"a")
    # need to update the rvt file as well
    for upObs_NM in upSF:
        obs_rvt_file_path = (
            "\n"
            + ":RedirectToFile    "
            + "./obs/"
            + upObs_NM
            + "_"
            + "discharge"
            + ".rvt"
        )

        WriteStringToFile(
            obs_rvt_file_path+'\n \n',Model_rvt_file_path,"a")
        #=============================================
        # copy the file
        os.system(
            'cp -r '+ObsDir+'/'+upObs_NM+'_discharge.rvt '+
            './RavenInput/obs/'+upObs_NM+'_discharge.rvt'
        )
        #=============================================
        # Typically rvt files in  ./RavenInput/obs/
        obs_rvt_file= './RavenInput/obs/'+upObs_NM+"_discharge.rvt"
        Replace1    = r'ObservationData\s+HYDROGRAPH'
        Replace2    = 'BasinInflowHydrograph'
        replace_SubID_save(obs_rvt_file, Replace1, Replace2, obs_rvt_file)

if len(upRS) > 0:
    WriteStringToFile(
    '# Inflow - ReservoirTargetStage\n \n',Model_rvt_file_path,"a")
    # need to update the rvt file as well
    for upObs_NM in upRS:
        obs_rvt_file_path = (
            "\n"
            + ":RedirectToFile    "
            + "./obs/"
            + upObs_NM
            + "_"
            + "level"
            + ".rvt"
        )

        WriteStringToFile(
            obs_rvt_file_path+'\n \n',Model_rvt_file_path,"a")
        #=============================================
        # copy the file
        os.system(
            'cp -r '+ObsDir+'/'+upObs_NM+'_level.rvt '+
            './RavenInput/obs/'+upObs_NM+'_level.rvt'
        )
        #=============================================
        # Typically rvt files in  ./RavenInput/obs/
        obs_rvt_file= './RavenInput/obs/'+upObs_NM+"_level.rvt"
        Replace1    = r'ObservationData\s+RESERVOIR_STAGE'
        Replace2    = 'ReservoirTargetStage'
        replace_SubID_save(obs_rvt_file, Replace1, Replace2, obs_rvt_file)