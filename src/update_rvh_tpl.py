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
#===================
Obs_NM=pm.Obs_NM() #sys.argv[1]
SubId=pm.SubId() #sys.argv[2]
ObsType=pm.ObsType() #sys.argv[3]
rvh_tpl='./'+pm.ModelName()+'.rvh.tpl' # sys.argv[4] #'./SE.rvh.tpl'
with open(rvh_tpl,'a') as f:
    f.write('\n'                                                                                            )
    f.write('\n# GAUGE specific subbasins'                                                                  )                                                                
    f.write('\n:PopulateSubBasinGroup UpstreamOf'+Obs_NM+' With Allsubbasins UPSTREAM_OF '+str(SubId)       )
    f.write('\n:PopulateSubBasinGroup NotUpstreamOf'+Obs_NM+' With Allsubbasins NOTWITHIN UpstreamOf'+Obs_NM)
    f.write('\n'                                                                                            )
    f.write('\n# Disable'                                                                                   )
    f.write('\n:DisableSubBasinGroup NotUpstreamOf'+Obs_NM                                                  )
    f.write('\n'                                                                                            )
    f.write('\n# parameters to calibrate'                                                                   )
    f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       MANNINGS_N             n_multi'      )
    f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       Q_REFERENCE            q_multi'      ) 
    f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RESERVOIR_CREST_WIDTH  k_multi'      )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       MANNINGS_N             n_multi'              )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       Q_REFERENCE            q_multi'              ) 
    # f.write('\n:SBGroupPropertyMultiplier   AllLakesubbasins   RESERVOIR_CREST_WIDTH  k_multi'              )
    # if observations is a lake --> calibrate individual CW
    if ObsType == 'RS':
        f.write('\n:SubBasinGroup   '+Obs_NM                                                                )
        f.write('\n\t'+str(SubId)                                                                           )
        f.write('\n:EndSubBasinGroup'                                                                       )
