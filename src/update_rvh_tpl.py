#! /usr/bin/python
#! utf+8
'''
update_rvh_tpl.py: update the rvh.tpl file
'''
import pandas as pd 
import numpy as np 
import os
import sys
import params as pm
#================================================================
def read_subid(fname):
    """Extracts the station ID from the ObservationData line, handling variable keywords."""
    with open(fname, 'r') as f:
        text=f.read()

    match = re.search(r'ObservationData\s+\S+\s+(\d+)', text)
    return int(match.group(1)) if match else 0
#================================================================
Obs_NM=pm.Obs_NM() #sys.argv[1]
SubId=pm.SubId() #sys.argv[2]
ObsType=pm.ObsType() #sys.argv[3]
BasinType=pm.BasinType()
#================================================================
# read input 
CWList = sys.argv[1]
if CWList == '':
    CWList='/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
CWList = pd.read_csv(CWList)
#================================================================
rvh_tpl='./'+pm.ModelName()+'.rvh.tpl' # sys.argv[4] #'./SE.rvh.tpl'
with open(rvh_tpl,'a') as f:
    f.write('\n'                                                                                            )
    f.write('\n# GAUGE specific subbasins'                                                                  )                                                                
    f.write('\n:PopulateSubBasinGroup UpstreamOf'+Obs_NM+' With SUBBASINS UPSTREAM_OF '+str(SubId)          )
    f.write('\n:PopulateSubBasinGroup NotUpstreamOf'+Obs_NM+' With SUBBASINS NOTWITHIN UpstreamOf'+Obs_NM   )
    f.write('\n'                                                                                            )
    f.write('\n# Disable'                                                                                   )
    f.write('\n:DisableSubBasinGroup NotUpstreamOf'+Obs_NM                                                  )
    f.write('\n'                                                                                            )
    f.write('\n# parameters to calibrate'                                                                   )
    f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       MANNINGS_N             n_multi'      )
    f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       Q_REFERENCE            q_multi'      )
    #================================================================
    # Bias Correction
    if pm.BiasCorrection():
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RAIN_CORR              p_multi'  )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RECHARGE_CORR          r_multi'  ) 
    #================================================================
    # Catchment Routing
    if pm.calCatRoute():
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       TIME_CONC              t_multi'  )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       TIME_TO_PEAK           t_multi'  )
    #================================================================
    # f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RESERVOIR_CREST_WIDTH  k_multi'      )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       MANNINGS_N             n_multi'              )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       Q_REFERENCE            q_multi'              ) 
    # f.write('\n:SBGroupPropertyMultiplier   AllLakesubbasins   RESERVOIR_CREST_WIDTH  k_multi'              )
    # if observations is a lake --> calibrate individual CW
    #================================================================
    if ObsType == 'RS':
        f.write('\n:SubBasinGroup   Lake_'+Obs_NM                                                            )
        f.write('\n\t'+str(SubId)                                                                            )
        f.write('\n:EndSubBasinGroup'                                                                        )    
        f.write('\n:PopulateSubBasinGroup NonLake'+Obs_NM+' With UpstreamOf'+Obs_NM+' NOTWITHIN Lake_'+Obs_NM)
        f.write('\n:SBGroupPropertyMultiplier   NonLake'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_multi'     )
        if pm.CWindv() == 'True':
            f.write('\n:SBGroupPropertyOverride     Lake_'+Obs_NM+'          RESERVOIR_CREST_WIDTH  w_'+Obs_NM   ) 
        # f.write('\n:SBGroupPropertyMultiplier   Lake_'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_'+Obs_NM   ) 
    elif ObsType == 'SF' and SubId in CWList['SubBasinID'].values:
        f.write('\n:SubBasinGroup   Lake_'+Obs_NM                                                            )
        f.write('\n\t'+str(SubId)                                                                            )
        f.write('\n:EndSubBasinGroup'                                                                        )    
        f.write('\n:PopulateSubBasinGroup NonLake'+Obs_NM+' With UpstreamOf'+Obs_NM+' NOTWITHIN Lake_'+Obs_NM)
        f.write('\n:SBGroupPropertyMultiplier   NonLake'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_multi'     )
        if pm.CWindv() == 'True':
            f.write('\n:SBGroupPropertyOverride     Lake_'+Obs_NM+'          RESERVOIR_CREST_WIDTH  w_'+Obs_NM   ) 
        # f.write('\n:SBGroupPropertyMultiplier   Lake_'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_'+Obs_NM   ) 
    else:
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'      RESERVOIR_CREST_WIDTH  k_multi'   )
        # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       MANNINGS_N             n_multi'        )
    #================================================================
    # need to do
    if BasinType == 'Intermediate':
        for uonm, uoty, usid  in zip(pm.UpObsNMList(),pm.UpObsTypes(),pm.UpSubIds()):
            if uoty == 'RS':
                # Up_SubId --> read_subid {Need add global parameters}
                f.write('\n')
                f.write('\n# Intermediate Sub Basin - Observed lake level'                                                          )
                f.write('\n:SubBasinGroup   Lake_'+str(uonm)                                                  )
                f.write('\n\t'+str(usid)                                                                      )
                f.write('\n:EndSubBasinGroup'                                                                 )
                f.write('\n:SBGroupPropertyOverride   Lake_'+str(uonm)+'        RESERVOIR_CREST_WIDTH  '+str(CWList[CWList['Obs_NM']==uonm]['cal.CW'].values[0]))  
            # # elif uoty == 'SF':
            # #     if uonm is in CWList['Obs_NM'].dropna().values:
            # #         f.write('\n')
            # #         f.write('\n# Intermediate Sub Basin - Observed outflow'                                                          )
            # #         f.write('\n:SubBasinGroup   Lake_'+str(uonm)                                                  )
            # #         f.write('\n\t'+str(usid)                                                                      )
            # #         f.write('\n:EndSubBasinGroup'                                                                 )
            # #         f.write('\n:SBGroupPropertyOverride   Lake_'+str(uonm)+'        RESERVOIR_CREST_WIDTH  '+str(CWList[CWList['Obs_NM']==uonm]['cal.CW'].values[0]))              
                                                             