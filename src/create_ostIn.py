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

import params as pm
#================================================================
def read_cal_gagues(RavenDir, filename='SE.rvt'):
    # Define a regular expression pattern to match the desired lines
    pattern = r'^:RedirectToFile\s+\.\/obs\/(.*?)(?<!_weight)\.rvt'
    # pattern = r'^:RedirectToFile\s+\.\/obs\/(.*?)(?<!_weight)(?<!_discharge)(?<!_level)\.rvt'

    # Open the file and read its lines
    with open(RavenDir+"/"+filename, 'r') as file:
        lines = file.readlines()

    # Extract values matching the pattern starting from line 39
    values = []
    tags = []
    skip_lines = False
    for line in lines[30:]:
        # print (line)
        if '# Streamflow' in line:
            tag='discharge'
        elif '# River Water Level' in line:
            tag='waterlevel'
        elif '# Reservoir Stage' in line:
            tag='reservoirstage'
        #==========
        # if 'weight' in line:
        #     skip_lines = True
        #     continue
        # elif 'Weight' in line:
        #     skip_lines = True
        #     continue
        # elif '#' in line:
        #     skip_lines = True
        #     continue
        # elif 'Inflow' in line:
        #     skip_lines = True
        #     break

        if '# Inflow' in line:
            break  # Stop reading after encountering "# Inflow"

        if any(keyword in line for keyword in ('weight', 'Weight', '#')):
            skip_lines = True
            continue

        # print (linek)
        # if skip_lines:
        #     break
        
        match = re.match(pattern, line)
        if match:
            values.append(match.group(1))
            tags.append(tag)
    return values, tags
#================================================================
def read_evaluation_met(RavenDir, filename='SE.rvi'):
    # Define a regular expression pattern to match the desired line
    pattern = r'^:EvaluationMetrics\s+(.*)$'

    # Open the file and read its lines
    with open(RavenDir+"/"+filename, 'r') as file:
        lines = file.readlines()

    # Extract the list of evaluation metrics
    evaluation_metrics = []
    for line in lines:
        match = re.match(pattern, line)
        if match:
            evaluation_metrics = match.group(1).split()

    # return list of evaluation metrics
    return evaluation_metrics
#================================================================
def get_suffix(RavenMet):
    metDict={
        'KLING_GUPTA':'KGE',
        'KLING_GUPTA_DEVIATION': 'KGD',
        'KLING_GUPTA_PRIME':'KGP',
        'KLING_GUPTA_DEVIATION_PRIME': 'KDP',
        'R2': 'R2'
    }
    return metDict[RavenMet]
#================================================================
def get_metric(tag):
    metDict={
        'discharge':'KLING_GUPTA',
        'waterlevel': 'KLING_GUPTA_DEVIATION',
        'reservoirstage':'KLING_GUPTA_DEVIATION'
    }
    return metDict[tag]
#================================================================
def divide_chunks(l, n): 
    # Yield successive n-sized 
    # chunks from l. 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]
#================================================================
def write_chunks(f, list_data, prefix):
    """
    Writes data in chunks to a file.

    Args:
        f: File object to write to.
        list_data: List of items to write.
        prefix: Prefix for labeling each chunk.
    """
    if len(list_data) >= 1:
        f.write('\n')
        # Split list into chunks of size 10
        list_chunks = list(divide_chunks(list_data, 10))
        for i, chunk in enumerate(list_chunks, start=1):
            f.write('\n\t' + f'{prefix}{i:1d}{len(chunk):8d}{5*" "}' +
                    '  '.join(chunk) +
                    '  wsum  ' + '  '.join(['-1'] * len(chunk)))
        # Write summary for all chunks
        f.write('\n\t' + f'{prefix}{len(list_chunks):9d}{5*" "}' +
                '  '.join([f'{prefix}{k}' for k in range(1, len(list_chunks) + 1)]) +
                '  wsum  ' + '  '.join(['1'] * len(list_chunks)))
    # elif len(list_data) >= 1:
    #     f.write('\n\t' + f'{prefix}{len(list_data):9d}{5*" "}' +
    #             '  '.join([f'{prefix}{k}' for k in range(1, len(list_data) + 1)]) +
    #             '  wsum  ' +'  '.join(['1'] * len(list_data)))

#=================================================================================================
def mk_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        pass
#================================================================================================
def write_ostIN_serial(
    OstrichRavenDir,
    filename='ostIn.txt',
    RunName='SE',
    progType='DDS',
    objFunc='GCOP',
    CWindv=True,
    BiasCor=True,
    costFunc='NegMET',
    MaxIter='2',
    w1=1.0,
    w2=1.0,
    w3=1.0
    ):
    #================================================================
    # serial 
    RandomSeed=random.randint(1000000, 1000000000)
    #================================================================
    # mk_dir(OstrichRavenDir)
    RavenDir=os.path.join(OstrichRavenDir,'RavenInput')
    #================================================================
    # for tag in ['serial', 'MPI']:
    ostin=os.path.join(OstrichRavenDir,filename)
    with open(ostin, 'w') as f:
        f.write(     'ProgramType          '+str(progType)                 )
        f.write('\n'+'ObjectiveFunction    '+str(objFunc)                  )
        f.write('\n'+'ModelExecutable      ./Ost-Raven.sh'                 )
        f.write('\n'+'PreserveBestModel    ./save_best.sh'                 )
        f.write('\n'+'#OstrichWarmStart      yes'                          )
        f.write('\n'+''                                                    )
        f.write('\n'+'BeginExtraDirs'                                      )
        f.write('\n'+'  RavenInput'                                        )
        f.write('\n'+'  #best'                                             )
        f.write('\n'+'EndExtraDirs'                                        )
        f.write('\n'+''                                                    )
        f.write('\n'+'BeginFilePairs'                                      )
        f.write('\n'+'  '+RunName+'.rvp.tpl;                '+RunName+'.rvp')
        f.write('\n'+'  '+RunName+'.rvh.tpl;                '+RunName+'.rvh')
        # if lake rvh needed to be calibrated
        # f.write('\n'+'  #crest_width_par.csv.tpl;     crest_width_par.csv' )
        # f.write('\n'+'  #SE.rvc.tpl;                  SE.rvc'              )
        f.write('\n'+''                                                    )
        f.write('\n'+'#can be multiple (.rvh, .rvi)'                       )
        f.write('\n'+'EndFilePairs'                                        )
        #==============================================================
        # parameters
        #==============================================================
        # Soil Parameters + Routing Parameters
        f.write('\n')
        f.write('\n')
        f.write('#Parameter    Specification')
        f.write('\n')
        f.write('\n'+'BeginParams')
        f.write('\n'+'#parameter                init.        low        high         tx_in    tx_ost    tx_out    format')
        #-----------------------------------------------------------------------------------------
        ## Soil parameters
        f.write('\n'+'## SOIL')    
        # f.write('\n'+'%Rain_Snow_T%             random       -2         2            none    none    none')
        # f.write('\n'+'%TOC_MUL%                 random       0          6            none    none    none')
        # f.write('\n'+'%TTP_MUL%                 random       0          6            none    none    none')
        # f.write('\n'+'%G_SH_MUL%                random       0          6            none    none    none')
        # f.write('\n'+'%G_SC_MUL%                random       0          6            none    none    none')
        # f.write('\n')
        # f.write('\n'+'%PET_CORRECTION%          random       0.5        1.5          none    none    none')
        f.write('\n'+'%MAX_BASEFLOW_RATE%       random       0          20           none    none    none')
        f.write('\n'+'%BASEFLOW_N%              random       0.1        4.0          none    none    none')
        # f.write('\n'+'%BASE_T%                  random       0.5        0.99         none    none    none')
        # f.write('\n')
        # f.write('\n'+'%LAKE_PET_CORR%           random       0.5        1.5          none    none    none')
        # f.write('\n'+'%WIND_VEL_CORR%           random       0.5        1.5          none    none    none')
        # f.write('\n'+'%RELHUM_CORR%             random       0.5        1.5          none    none    none')
        # f.write('\n')
        #-----------------------------------------------------------------------------------------
        ## Bias correction
        if BiasCor:  
            f.write('\n')
            f.write('\n'+'## BIAS CORRECTION FACTORS')
            f.write('\n'+'p_multi                   random       0.1         2.0           none    none    none   # rain correction factor for subbasin'                )
            f.write('\n'+'r_multi                   random       0.1         2.0           none    none    none   # recharge correction factor for subbasin'            )  
        #-----------------------------------------------------------------------------------------
        ## Routing parameters
        f.write('\n')
        f.write('\n'+'## ROUTING')
        f.write('\n'+'n_multi                   random       0.1        10.0           none    none    none   # manning`s n'                )
        f.write('\n'+'q_multi                   random       0.1        10.0           none    none    none   # Q_reference'                )
        f.write('\n'+'k_multi                   random       0.1         2.0           none    none    none   # lake crest width multiplier')
        #-----------------------------------------------------------------------------------------
        ## Routing parameters
        # f.write('\n')
        # f.write('\n'+'## ROUTING')
        # f.write('\n'+'c_multi                   random       0.1        10           none    none    none   # celerity'                   )
        # f.write('\n'+'d_multi                   random       0.1        10           none    none    none   # diffusivity'                )
        # f.write('\n'+'k_multi                   random       0.1        10           none    none    none   # lake crest width multiplier')
        #-----------------------------------------------------------------------------------------
        gnames, tags = read_cal_gagues(RavenDir)
        #-----------------------------------------------------------------------------------------
        # print ('CWindv',CWindv)
        if CWindv:
            print ('Calibrate Indvidual CW', 'w_'+'%-24s'%(str(gnames[0].split('_')[0])))
            if pm.InitCW() != -9999.0:
                f.write('\n')
                f.write('\n'+'## Individual Lake CW multipler')
                lowb = min(float(pm.InitCW())*0.1,0.01)
                upb  = max(float(pm.InitCW())*2.0,10.0)
                f.write('\nw_'+'%-24s'%(str(gnames[0].split('_')[0]))+'random       '+'%5.2f'%(lowb)+'        '+'%5.2f'%(upb)+'          none    none    none   #'+str(gnames[0].split('_')[0]))
                # print ('\nw_'+'%-24s'%(str(gnames[0].split('_')[0]))+'random       '+'%5.2f'%(lowb)+'        '+'%5.2f'%(upb)+'          none    none    none   #'+str(gnames[0].split('_')[0]))
            # if 'reservoirstage' in tags:
            #     indices = [i for i, tag in enumerate(tags) if tag == 'reservoirstage']
            #     f.write('\n')
            #     f.write('\n'+'## Individual Lake CW multipler')
            #     for index in indices:
            #         lowb = max(float(pm.InitCW())*0.1,0.1)
            #         upb  = max(float(pm.InitCW())*2.0,10.0)
            #         f.write('\nw_'+'%-24s'%(str(gnames[index].split('_')[0]))+'random       '+'%5.2f'%(lowb)+'        '+'%5.2f'%(upb)+'          none    none    none   #'+str(gnames[index].split('_')[0]))
        #-----------------------------------------------------------------------------------------
        f.write('\n'+'EndParams')
        #-----------------------------------------------------------------------------------------
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginResponseVars')
        f.write('\n'+'#name                                                         filename  keyword       line     col     token')
        #-----------------------------------------------------------------------------------------
        Eval_list=read_evaluation_met(RavenDir)
        #-----------------------------------------------------------------------------------------
        distag=0
        wltag=0
        rstag=0
        SF_list=[]
        WL_list=[]
        RS_list=[]
        #-----------------------------------------------------------------------------------------
        lineN=1
        for gau_nm,  tag in zip(gnames, tags):
            RavenMet=get_metric(tag)
            suffix=get_suffix(RavenMet)
            # gauge=gau_nm.split('_')[0]
            gauge=gau_nm.split('_')[0].replace(' ', '_')
            # print (RavenMet, suffix)
            if tag == 'discharge':
                if distag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [Discharge]')
                distag=distag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                SF_list.append(gName)
            elif tag == 'waterlevel':
                if wltag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [River Water Level]')
                wltag=wltag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                WL_list.append(gName)
            elif tag =='reservoirstage':
                if rstag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [Reservoir Stage]')
                rstag=rstag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                RS_list.append(gName)
            #----------------------
            # create the name
            #----------------------
            f.write('\n%-26s./RavenInput/output/SE_Diagnostics.csv; OST_NULL%10d%10d%10s'%(gName,lineN,colN,"','"))
            lineN=lineN+1
        f.write('\n')
        f.write('\n'+'EndResponseVars')
        #==============================================================
        # Tied Response Vars
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginTiedRespVars')
        f.write('\n\t'+'# <name1> <np1> <pname1,1> <pname1,2> ... <pname1,np1> <type1> <type_data1>')
        #---------------------------------------------------------------
        # Writing SF_list, WL_list, and RS_list
        write_chunks(f, SF_list, "NegKGE_Q")
        write_chunks(f, WL_list, "NegKGD_WL")
        write_chunks(f, RS_list, "NegKGD_RS")
            
        # # # if len(SF_list)>=1:
        # # #     # make chucks
        # # #     f.write('\n')
        # # #     SF_list_chuncks=list(divide_chunks(SF_list, 10))
        # # #     # print (SF_list_chuncks)
        # # #     for i, chunck in enumerate(SF_list_chuncks, start=1):
        # # #         # print (chunck)
        # # #         f.write('\n\t'+'NegKGE_Q%d%8d%5s'%(i,len(chunck),' ')+
        # # #         '  '.join(chunck)+
        # # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # # #     f.write('\n\t'+'NegKGE_Q%9d%5s'%(len(SF_list_chuncks),' ')+
        # # #     '  '.join(['NegKGE_Q%d'%(k) for k in range(1,len(SF_list_chuncks)+1)])+
        # # #     '  wsum  '+ '  '.join(['1']*len(SF_list_chuncks)))
        # # # #---------------------------------------------------------------
        # # # if len(WL_list)>=1:
        # # #     # make chucks
        # # #     f.write('\n')
        # # #     WL_list_chuncks=list(divide_chunks(WL_list, 10))
        # # #     # print (WL_list_chuncks)
        # # #     for i, chunck in enumerate(WL_list_chuncks, start=1):
        # # #         # print (chunck)
        # # #         f.write('\n\t'+'NegKGD_WL%d%8d%5s'%(i,len(chunck),' ')+
        # # #         '  '.join(chunck)+
        # # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # # #     f.write('\n\t'+'NegKGD_WL%9d%5s'%(len(WL_list_chuncks),' ')+
        # # #     '  '.join(['NegKGD_WL%d'%(k) for k in range(1,len(WL_list_chuncks)+1)])+
        # # #     '  wsum  '+ '  '.join(['1']*len(WL_list_chuncks)))
        # # # #---------------------------------------------------------------
        # # # if len(RS_list)>=1:
        # # #     # make chucks
        # # #     f.write('\n')
        # # #     RS_list_chuncks=list(divide_chunks(RS_list, 10))
        # # #     # print (RS_list_chuncks)
        # # #     for i, chunck in enumerate(RS_list_chuncks, start=1):
        # # #         # print (chunck)
        # # #         f.write('\n\t'+'NegKGD_RS%d%8d%5s'%(i,len(chunck),' ')+
        # # #         '  '.join(chunck)+
        # # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # # #     f.write('\n\t'+'NegKGD_RS%9d%5s'%(len(RS_list_chuncks),' ')+
        # # #     '  '.join(['NegKGD_RS%d'%(k) for k in range(1,len(RS_list_chuncks)+1)])+
        # # #     '  wsum  '+ '  '.join(['1']*len(RS_list_chuncks)))
        #---------------------------------------------------------------
        # calculate 
        nq=len(SF_list)
        nwl=len(WL_list)
        nwa=len(RS_list)
        nt=nq+nwl+nwa
        # Define weights and labels
        components = [
            ('NegKGE_Q', len(SF_list), w1 * (float(nq) / float(nt))),
            ('NegKGD_WL', len(WL_list), w2 * (float(nwl) / float(nt))),
            ('NegKGD_RS', len(RS_list), w3 * (float(nwa) / float(nt))),
        ]
        # Filter valid components
        valid_components = [(label, weight) for label, count, weight in components if count >= 1]

        #---------------------------------------------------------------
        # final objective function
        # Write based on the number of valid components
        if valid_components:
            labels, weights = zip(*valid_components)  # Unpack labels and weights
            num_components = len(labels)  # Number of valid components

            # Build the dynamic format string
            label_format = ''.join(['%15s' for _ in range(num_components)])
            weight_format = ''.join(['%8.3f' for _ in range(num_components)])
            full_format = f'\n\n\t%-16s%2d{label_format}%8s{weight_format}'

            # Write to the file
            f.write(full_format % (
                str(costFunc), num_components, *labels, 'wsum', *weights
            ))

        # # #---------------------------------------------------------------
        # # # final objective function
        # # if len(RS_list)>=1 and len(WL_list)>=1 and len(SF_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),3,'NegKGE_Q',
        # #     'NegKGD_WL','NegKGD_RS','wsum',
        # #     w1*(float(nq)/float(nt)),w2*(float(nwl)/float(nt)),w3*(float(nwa)/float(nt))))
        # # elif len(WL_list)>=1 and len(SF_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),2,'NegKGE_Q',
        # #     'NegKGD_WL','wsum',
        # #     w1*(float(nq)/float(nt)),w2*(float(nwl)/float(nt))))
        # # elif len(RS_list)>=1 and len(SF_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),2,'NegKGE_Q',
        # #     'NegKGD_RS','wsum',
        # #     w1*(float(nq)/float(nt)),w3*(float(nwa)/float(nt))))
        # # elif len(WL_list)>=1 and len(RS_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),2,'NegKGD_WL',
        # #     'NegKGD_RS','wsum',
        # #     w2*(float(nwl)/float(nt)),w3*(float(nwa)/float(nt))))
        # # elif len(SF_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),1,'NegKGE_Q',
        # #     'wsum',
        # #     w1*(float(nq)/float(nt))))
        # # elif len(WL_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),1,'NegKGD_WL',
        # #     'wsum',
        # #     w2*(float(nwl)/float(nt))))
        # # elif len(RS_list)>=1:
        # #     f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),1,'NegKGD_RS',
        # #     'wsum',
        # #     w3*(float(nwa)/float(nt))))
        #---------------------------------------------------------------
        # 0.334*(1.0/float(len(SF_list))),0.333*(1.0/float(len(WL_list))),0.333*(1.0/float(len(RS_list)))))
        #---------------------------------------------------------------
        f.write('\n')
        f.write('\n'+'EndTiedRespVars')
        #==============================================================
        # Constraints
        #==============================================================
        f.write('\n')
        f.write('\n'+'BeginConstraints')
        f.write('\n\t'+'#name type    conv.fact  lower   upper  resp.var')
        f.write('\n'+'EndConstraints')
        #==============================================================
        # RandomSeed
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'RandomSeed%15s'%(str(RandomSeed)))
        #==============================================================
        # GOCP
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginGCOP')
        f.write('\n\t'+'CostFunction%15s'%(str(costFunc)))
        f.write('\n\t'+'PenaltyFunction  APM')
        f.write('\n'+'EndGCOP')
        #==============================================================
        # DDSAlg
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginDDSAlg')
        f.write('\n\t'+'PerturbationValue   0.20')
        f.write('\n\t'+'MaxIterations%10s'%(str(MaxIter)))
        f.write('\n\t'+'# UseInitialParamValues')
        f.write('\n\t'+'# above initializes DDS to parameter values IN the initial model input files')
        f.write('\n'+'EndDDSAlg')

#================================================================================================
def write_ostIN_parallel(
    OstrichRavenDir,
    filename='ostIn.txt',
    RunName='SE',
    progType='ParallelDDS',
    objFunc='GCOP',
    CWindv=True,
    BiasCor=True,
    calCatRoute=True,
    costFunc='NegMET',
    MaxIter='500',
    w1=1.0,
    w2=1.0,
    w3=1.0
    ):
    #================================================================================================
    # MPI 
    RandomSeed=random.randint(1000000, 1000000000)
    #================================================================
    # mk_dir(OstrichRavenDir)
    RavenDir=os.path.join(OstrichRavenDir,'RavenInput')
    #================================================================
    ostin=os.path.join(OstrichRavenDir,filename)
    with open(ostin, 'w') as f:
        f.write(     'ProgramType          '+str(progType)                 )
        f.write('\n'+'ObjectiveFunction    '+str(objFunc)                  )
        f.write('\n'+'ModelExecutable      ./Ost-Raven.sh'                 )
        f.write('\n'+'PreserveBestModel    ./save_best.sh'                 )
        f.write('\n'+'#OstrichWarmStart      yes'                          )
        f.write('\n'+''                                                    )
        f.write('\n'+'ModelSubdir processor_'                              )
        f.write('\n'+''                                                    )    
        f.write('\n'+'BeginExtraDirs'                                      )
        f.write('\n'+'  RavenInput'                                        )
        f.write('\n'+'  #best'                                             )
        f.write('\n'+'EndExtraDirs'                                        )
        f.write('\n'+''                                                    )
        f.write('\n'+'BeginFilePairs'                                      )
        f.write('\n'+'  SE.rvp.tpl;                  SE.rvp'               )
        f.write('\n'+'  SE.rvh.tpl;                  SE.rvh'               )
        # f.write('\n'+'  #crest_width_par.csv.tpl;     crest_width_par.csv' )
        # f.write('\n'+'  #SE.rvc.tpl;                  SE.rvc'              )
        f.write('\n'+''                                                    )
        f.write('\n'+'#can be multiple (.rvh, .rvi)'                       )
        f.write('\n'+'EndFilePairs'                                        )
        #==============================================================
        # parameters
        #==============================================================
        # Soil Parameters + Routing Parameters
        f.write('\n')
        f.write('\n')
        f.write('#Parameter    Specification')
        f.write('\n')
        f.write('\n'+'BeginParams')
        f.write('\n'+'#parameter                init.        low        high         tx_in    tx_ost    tx_out    format')
        #-----------------------------------------------------------------------------------------
        ## Soil parameters
        f.write('\n'+'## SOIL')    
        # f.write('\n'+'%Rain_Snow_T%             random       -2         2            none    none    none')
        # f.write('\n'+'%TOC_MUL%                 random       0          6            none    none    none')
        # f.write('\n'+'%TTP_MUL%                 random       0          6            none    none    none')
        # f.write('\n'+'%G_SH_MUL%                random       0          6            none    none    none')
        # f.write('\n'+'%G_SC_MUL%                random       0          6            none    none    none')
        # f.write('\n')
        # f.write('\n'+'%PET_CORRECTION%          random       0.5        1.5          none    none    none')
        f.write('\n'+'%MAX_BASEFLOW_RATE%       random       0          20           none    none    none')
        f.write('\n'+'%BASEFLOW_N%              random       0.1        4.0          none    none    none')
        # f.write('\n'+'%BASE_T%                  random       0.5        0.99         none    none    none')
        # f.write('\n')
        # f.write('\n'+'%LAKE_PET_CORR%           random       0.5        1.5          none    none    none')
        # f.write('\n'+'%WIND_VEL_CORR%           random       0.5        1.5          none    none    none')
        # f.write('\n'+'%RELHUM_CORR%             random       0.5        1.5          none    none    none')
        # f.write('\n')
        #-----------------------------------------------------------------------------------------
        ## Bias correction
        if BiasCor:
            f.write('\n')
            f.write('\n'+'## BIAS CORRECTION FACTORS')
            f.write('\n'+'p_multi                   random       0.1         2.0           none    none    none   # rain correction factor for subbasin'                )
            f.write('\n'+'r_multi                   random       0.1         2.0           none    none    none   # recharge correction factor for subbasin'            ) 
        #-----------------------------------------------------------------------------------------
        ## Calibrate Catchment Routing
        if calCatRoute: 
            f.write('\n')
            f.write('\n'+'## CATCHMENT ROUTING')
            f.write('\n'+'t_multi                   random       0.0       100.0           none    none    none   # for ROUTE_TRI_CONVOLUTION'                          )
        #-----------------------------------------------------------------------------------------
        ## Routing parameters
        f.write('\n')
        f.write('\n'+'## ROUTING')
        f.write('\n'+'n_multi                   random       0.1        10.0           none    none    none   # manning`s n'                )
        f.write('\n'+'q_multi                   random       0.1        10.0           none    none    none   # celerity'                   )
        f.write('\n'+'k_multi                   random       0.1         2.0           none    none    none   # lake crest width multiplier')
        #-----------------------------------------------------------------------------------------
        # ## Routing parameters
        # f.write('\n')
        # f.write('\n'+'## ROUTING')
        # f.write('\n'+'c_multi                   random       0.1        10           none    none    none   # celerity'                   )
        # f.write('\n'+'d_multi                   random       0.1        10           none    none    none   # diffusivity'                )
        # f.write('\n'+'k_multi                   random       0.1        10           none    none    none   # lake crest width multiplier')
        #-----------------------------------------------------------------------------------------
        gnames, tags = read_cal_gagues(RavenDir)
        #-----------------------------------------------------------------------------------------
        if CWindv:
            if pm.InitCW() != -9999.0:
                f.write('\n')
                f.write('\n'+'## Individual Lake CW multipler')
                lowb = min(float(pm.InitCW())*0.1,0.01)
                upb  = max(float(pm.InitCW())*2.0,10.0)
                f.write('\nw_'+'%-24s'%(str(gnames[0].split('_')[0]))+'random       '+'%5.2f'%(lowb)+'        '+'%5.2f'%(upb)+'          none    none    none   #'+str(gnames[0].split('_')[0]))

            # if 'reservoirstage' in tags:
            #     indices = [i for i, tag in enumerate(tags) if tag == 'reservoirstage']
            #     f.write('\n')
            #     f.write('\n'+'## Individual Lake CW multipler')
            #     for index in indices:
            #         lowb = max(float(pm.InitCW())*0.1,0.1)
            #         upb  = max(float(pm.InitCW())*2.0,10.0)
            #         f.write('\nw_'+'%-24s'%(str(gnames[index].split('_')[0]))+'random       '+'%5.2f'%(lowb)+'        '+'%5.2f'%(upb)+'          none    none    none   #'+str(gnames[index].split('_')[0]))
        #-----------------------------------------------------------------------------------------
        f.write('\n'+'EndParams')
        #-----------------------------------------------------------------------------------------
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginResponseVars')
        f.write('\n'+'#name                                                         filename  keyword       line     col     token')
        #-----------------------------------------------------------------------------------------
        Eval_list=read_evaluation_met(RavenDir)
        #-----------------------------------------------------------------------------------------
        distag=0
        wltag=0
        rstag=0
        SF_list=[]
        WL_list=[]
        RS_list=[]
        #-----------------------------------------------------------------------------------------
        lineN=1
        for gau_nm,  tag in zip(gnames, tags):
            RavenMet=get_metric(tag)
            suffix=get_suffix(RavenMet)
            # gauge=gau_nm.split('_')[0]
            gauge=gau_nm.split('_')[0].replace(' ', '')
            # print (RavenMet, suffix)
            if tag == 'discharge':
                if distag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [Discharge]')
                distag=distag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                SF_list.append(gName)
            elif tag == 'waterlevel':
                if wltag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [River Water Level]')
                wltag=wltag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                WL_list.append(gName)
            elif tag =='reservoirstage':
                if rstag==0:
                    f.write('\n')
                    f.write('\n'+'# '+RavenMet+' [Reservoir Stage]')
                rstag=rstag+1
                colN=Eval_list.index(RavenMet)+1+2 # convert to starting from 1 + observed_data_series and filename coloums
                gName=suffix+'_'+str(gauge)
                RS_list.append(gName)
            #----------------------
            # create the name
            #----------------------
            f.write('\n%-26s./RavenInput/output/SE_Diagnostics.csv; OST_NULL%10d%10d%10s'%(gName,lineN,colN,"','"))
            print (gName,lineN,colN)
            lineN=lineN+1
        f.write('\n')
        f.write('\n'+'EndResponseVars')
        #==============================================================
        # Tied Response Vars
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginTiedRespVars')
        f.write('\n\t'+'# <name1> <np1> <pname1,1> <pname1,2> ... <pname1,np1> <type1> <type_data1>')
        #---------------------------------------------------------------
        # Writing SF_list, WL_list, and RS_list
        write_chunks(f, SF_list, "NegKGE_Q")
        write_chunks(f, WL_list, "NegKGD_WL")
        write_chunks(f, RS_list, "NegKGD_RS")

        # # if len(SF_list)>=1:
        # #     # make chucks
        # #     f.write('\n')
        # #     SF_list_chuncks=list(divide_chunks(SF_list, 10))
        # #     # print (SF_list_chuncks)
        # #     for i, chunck in enumerate(SF_list_chuncks, start=1):
        # #         # print (chunck)
        # #         f.write('\n\t'+'NegKGE_Q%d%8d%5s'%(i,len(chunck),' ')+
        # #         '  '.join(chunck)+
        # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # #     f.write('\n\t'+'NegKGE_Q%9d%5s'%(len(SF_list_chuncks),' ')+
        # #     '  '.join(['NegKGE_Q%d'%(k) for k in range(1,len(SF_list_chuncks)+1)])+
        # #     '  wsum  '+ '  '.join(['1']*len(SF_list_chuncks)))
        # # #---------------------------------------------------------------
        # # if len(WL_list)>=1:
        # #     # make chucks
        # #     f.write('\n')
        # #     WL_list_chuncks=list(divide_chunks(WL_list, 10))
        # #     # print (WL_list_chuncks)
        # #     for i, chunck in enumerate(WL_list_chuncks, start=1):
        # #         # print (chunck)
        # #         f.write('\n\t'+'NegKGD_WL%d%8d%5s'%(i,len(chunck),' ')+
        # #         '  '.join(chunck)+
        # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # #     f.write('\n\t'+'NegKGD_WL%9d%5s'%(len(WL_list_chuncks),' ')+
        # #     '  '.join(['NegKGD_WL%d'%(k) for k in range(1,len(WL_list_chuncks)+1)])+
        # #     '  wsum  '+ '  '.join(['1']*len(WL_list_chuncks)))
        # # #---------------------------------------------------------------
        # # if len(RS_list)>=1:
        # #     # make chucks
        # #     f.write('\n')
        # #     RS_list_chuncks=list(divide_chunks(RS_list, 10))
        # #     # print (RS_list_chuncks)
        # #     for i, chunck in enumerate(RS_list_chuncks, start=1):
        # #         # print (chunck)
        # #         f.write('\n\t'+'NegKGD_RS%d%8d%5s'%(i,len(chunck),' ')+
        # #         '  '.join(chunck)+
        # #         '  wsum  '+ '  '.join(['-1']*len(chunck)))
        # #     f.write('\n\t'+'NegKGD_RS%9d%5s'%(len(RS_list_chuncks),' ')+
        # #     '  '.join(['NegKGD_RS%d'%(k) for k in range(1,len(RS_list_chuncks)+1)])+
        # #     '  wsum  '+ '  '.join(['1']*len(RS_list_chuncks)))
        # calculate 
        nq=len(SF_list)
        nwl=len(WL_list)
        nwa=len(RS_list)
        nt=nq+nwl+nwa
        #  Define weights and labels
        components = [
            ('NegKGE_Q', len(SF_list), w1 * (float(nq) / float(nt))),
            ('NegKGD_WL', len(WL_list), w2 * (float(nwl) / float(nt))),
            ('NegKGD_RS', len(RS_list), w3 * (float(nwa) / float(nt))),
        ]
        # Filter valid components
        valid_components = [(label, weight) for label, count, weight in components if count >= 1]

        #---------------------------------------------------------------
        # final objective function
        # Write based on the number of valid components
        if valid_components:
            labels, weights = zip(*valid_components)  # Unpack labels and weights
            num_components = len(labels)  # Number of valid components

            # Build the dynamic format string
            label_format = ''.join(['%15s' for _ in range(num_components)])
            weight_format = ''.join(['%8.3f' for _ in range(num_components)])
            full_format = f'\n\n\t%-16s%2d{label_format}%8s{weight_format}'

            # Write to the file
            f.write(full_format % (
                str(costFunc), num_components, *labels, 'wsum', *weights
            ))
        # # #---------------------------------------------------------------
        # # # final objective function
        # # f.write('\n\n\t%-16s%2d%15s%15s%15s%8s%8.3f%8.3f%8.3f'%(str(costFunc),3,'NegKGE_Q',
        # # 'NegKGD_WL','NegKGD_RS','wsum',
        # # w1*(float(nq)/float(nt)),w2*(float(nwl)/float(nt)),w3*(float(nwa)/float(nt))))
        #---------------------------------------------------------------
        # 0.334*(1.0/float(len(SF_list))),0.333*(1.0/float(len(WL_list))),0.333*(1.0/float(len(RS_list)))))
        #---------------------------------------------------------------
        f.write('\n')
        f.write('\n'+'EndTiedRespVars')
        #==============================================================
        # Constraints
        #==============================================================
        f.write('\n')
        f.write('\n'+'BeginConstraints')
        f.write('\n\t'+'#name type    conv.fact  lower   upper  resp.var')
        f.write('\n'+'EndConstraints')
        #==============================================================
        # RandomSeed
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'RandomSeed%15s'%(str(RandomSeed)))
        #==============================================================
        # GOCP
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginGCOP')
        f.write('\n\t'+'CostFunction%15s'%(str(costFunc)))
        f.write('\n\t'+'PenaltyFunction  APM')
        f.write('\n'+'EndGCOP')
        #==============================================================
        # DDSAlg
        #==============================================================
        f.write('\n')
        f.write('\n')
        f.write('\n'+'BeginParallelDDSAlg')
        f.write('\n\t'+'PerturbationValue      0.2')
        f.write('\n\t'+'MaxIterations%10s'%(str(MaxIter)))
        f.write('\n\t'+'UseRandomParamValues')
        f.write('\n\t'+'UseOpt                 standard')
        f.write('\n'+'EndParallelDDSAlg')


#================================================================
# Read the SE.rvt file and get the lists of Streamflow, River Water Level, and Reservoir Stage
# RavenDir='/Volumes/MENAKA/1.Work/1.UWaterloo/1.Projects/P3.OntarioFloodPlain/OLRRP_Build_Raven/data/SEregion/Raven_inputs/RavenInput'
# RavenDir='/Volumes/MENAKA/1.Work/1.UWaterloo/1.Projects/P3.OntarioFloodPlain/OLRRP_Build_Raven/data/SE_v2-0-2_02KC015'
# RavenDir='/Volumes/MENAKA/1.Work/1.UWaterloo/1.Projects/P3.OntarioFloodPlain/OLRRP_Build_Raven/data/SE_v2-0-2_02LB018'
# print (read_cal_gagues(RavenDir))
# OstrichRavenDir=RavenDir #'/Volumes/MENAKA/1.Work/1.UWaterloo/1.Projects/P3.OntarioFloodPlain/OLRRP_Build_Raven/data/OstrichRaven'

para=int(sys.argv[1])

print ('\tCreate ostIn.txt')
print ('\t\t'+pm.CWindv(), pm.BiasCorrection(), pm.MaxIter())

if para>0:
    write_ostIN_parallel('./', CWindv=pm.CWindv(), BiasCor=pm.BiasCorrection(), calCatRoute=pm.calCatRoute(), MaxIter=pm.MaxIter()) # parallel
else:
    write_ostIN_serial('./', CWindv=pm.CWindv(), BiasCor=pm.BiasCorrection(), calCatRoute=pm.calCatRoute(), MaxIter=pm.MaxIter())   # serial