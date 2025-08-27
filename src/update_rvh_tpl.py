#! /usr/bin/python
#! utf+8
'''
update_rvh_tpl.py: update the rvh.tpl file
'''
import pandas as pd
import numpy as np
import os
import sys
import re
from logger import log
import params as pm
#================================================================
def get_cw_map(cw_df):
    """Create a dict for fast Obs_NM to CW lookup."""
    return cw_df.set_index('Obs_NM')['cal.CW'].to_dict()
#================================================================
def write_block(f, lines):
    """Writes a list of lines to file with newline separation."""
    f.write('\n' + '\n'.join(lines) + '\n')
#================================================================
def main():
    CWList = sys.argv[1] if len(sys.argv) > 1 else '/home/menaka/projects/def-btolson/menaka/MulCal/dat/LakeCWList.csv'
    cw_df = pd.read_csv(CWList)
    cw_map = get_cw_map(cw_df)
    subid_set = set(cw_df['SubBasinID'].values)

    rvh_tpl = f'./{pm.ModelName()}.rvh.tpl'
    with open(rvh_tpl, 'a') as f:
        Obs_NM = pm.Obs_NM()
        SubId = pm.SubId()
        ObsType = pm.ObsType()
        BasinType = pm.BasinType()

        lines = [
            # "",
            "# GAUGE specific subbasins",
            f":PopulateSubBasinGroup UpstreamOf{Obs_NM} With SUBBASINS UPSTREAM_OF {SubId}",
            f":PopulateSubBasinGroup NotUpstreamOf{Obs_NM} With SUBBASINS NOTWITHIN UpstreamOf{Obs_NM}",
            "",
            "# Disable",
            f":DisableSubBasinGroup NotUpstreamOf{Obs_NM}"
        ]

        # if BasinType == 'Intermediate':
        #     up_obs_nms = pm.UpObsNMList()
        #     up_sub_ids = pm.UpSubIds()
        #     lines.append("")
        #     lines.append("# Define subbasins bounded by upstream and downstream gauges")
        #     for uonm, usid in zip(up_obs_nms, up_sub_ids):
        #         lines.append(f":PopulateSubBasinGroup Exclude_{uonm} With SUBBASINS UPSTREAM_OF {usid}")
        #     lines.append("")
        #     lines.append(f":MergeSubBasinGroups Excluded_All From {' '.join(['Exclude_' + u for u in up_obs_nms])}")
        #     lines.append("")
        #     # lines.append(f":IntersectSubBasinGroups GaugedSubbasinGroup From UpstreamOf{Obs_NM} And NOTWITHIN Excluded_All")
        #     lines.append(f":PopulateSubBasinGroup GaugedSubbasinGroup With SUBBASINS NOTWITHIN Excluded_All")
        #     lines.append("# Gagued SubBasin Group")
        #     lines.append(":GaugedSubBasinGroup   GaugedSubbasinGroup")
        # else:
        #     lines.append("# Gagued SubBasin Group")
        #     lines.append(":GaugedSubBasinGroup   UpstreamOf" + Obs_NM)
        
        lines.append("# Gagued SubBasin Group")
        lines.append(":GaugedSubBasinGroup   UpstreamOf" + Obs_NM)

        # Routing and bias correction options
        if pm.calRivRoute():
            lines += [
                "",
                "# River Routing",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} MANNINGS_N n_multi",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} Q_REFERENCE q_multi"
            ]

        if pm.BiasCorrection():
            lines += [
                "",
                "# Bias Correction",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} RAIN_CORR p_multi",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} RECHARGE_CORR r_multi"
            ]

        if pm.calCatRoute():
            lines += [
                "",
                "# Catchment Routing",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} TIME_CONC t_multi",
                f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} TIME_TO_PEAK t_multi"
            ]

        # Crest Widths
        if pm.calLakeCW():
            log.info("Lake crest widths will be calibrated.")
            if ObsType == 'RS':
                lines += [
                    "",
                    f":SubBasinGroup   Lake_{Obs_NM}",
                    f"\t{SubId}",
                    ":EndSubBasinGroup",
                    f":PopulateSubBasinGroup NonLake{Obs_NM} With UpstreamOf{Obs_NM} NOTWITHIN Lake_{Obs_NM}",
                    f":SBGroupPropertyMultiplier NonLake{Obs_NM} RESERVOIR_CREST_WIDTH k_multi"
                ]
                if pm.CWindv():
                    lines.append(f":SBGroupPropertyOverride Lake_{Obs_NM} RESERVOIR_CREST_WIDTH w_{Obs_NM}")
            elif ObsType == 'SF' and SubId in subid_set:
                lines += [
                    "",
                    f":SubBasinGroup   Lake_{Obs_NM}",
                    f"\t{SubId}",
                    ":EndSubBasinGroup",
                    f":PopulateSubBasinGroup NonLake{Obs_NM} With UpstreamOf{Obs_NM} NOTWITHIN Lake_{Obs_NM}",
                    f":SBGroupPropertyMultiplier NonLake{Obs_NM} RESERVOIR_CREST_WIDTH k_multi"
                ]
                if pm.CWindv():
                    lines.append(f":SBGroupPropertyOverride Lake_{Obs_NM} RESERVOIR_CREST_WIDTH w_{Obs_NM}")
            else:
                lines.append(f":SBGroupPropertyMultiplier UpstreamOf{Obs_NM} RESERVOIR_CREST_WIDTH k_multi")

        write_block(f, lines)

        # Intermediate lakes
        if BasinType == 'Intermediate':
            for uonm, uoty, usid in zip(pm.UpObsNMList(), pm.UpObsTypes(), pm.UpSubIds()):
                if uoty == 'RS' and uonm in cw_map:
                    cw = cw_map[uonm]
                    write_block(f, [
                        "",
                        "# Intermediate Sub Basin - Observed lake level",
                        f":SubBasinGroup   Lake_{uonm}",
                        f"\t{usid}",
                        ":EndSubBasinGroup",
                        f":SBGroupPropertyOverride   Lake_{uonm} RESERVOIR_CREST_WIDTH {cw}"
                    ])
#================================================================
if __name__ == "__main__":
    main()




'''
import pandas as pd 
import numpy as np 
import os
import sys
from logger import log
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
    # make gauged subbasin
    if BasinType == 'Intermediate':
        f.write('\n# Define subbasins upstream of each of the excluded downstream points'                   )
        for uonm, usid  in zip(pm.UpObsNMList(),pm.UpSubIds()):
            f.write('\n:PopulateSubBasinGroup Exclude_'+uonm+' With SUBBASINS UPSTREAM_OF '+str(usid)       )
        f.write('\n# Merge all exclusions into one group'                                                   )
        f.write('\n:MergeSubBasinGroups Excluded_All From '+' '.join(['Exclude_'+uonm for uonm in pm.UpObsNMList()]))
        f.write('\n# Get subbasins that are in Upstream_'+Obs_NM+' but NOT in Excluded_All'                 )
        f.write('\n#:IntersectSubBasinGroups GaugedSubbasinGroup From UpstreamOf'+Obs_NM+' And NOTWITHIN Excluded_All')
        f.write('\n:PopulateSubBasinGroup GaugedSubbasinGroup With SUBBASINS NOTWITHIN Excluded_All'        )
        f.write('\n# Gagued SubBasin Group'                                                                 )
        f.write('\n:GaugedSubBasinGroup   GaugedSubbasinGroup'                                              )
    else:
        f.write('\n'                                                                                        )
        f.write('\n# Gagued SubBasin Group'                                                                 )

    #================================================================
    # River Routing
    if pm.calRivRoute():    
        f.write('\n# River Routing parameters'                                                              )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       MANNINGS_N             n_multi'  )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       Q_REFERENCE            q_multi'  )
    #================================================================
    # Bias Correction
    if pm.BiasCorrection():
        f.write('\n# Bias Correction'                                                                       )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RAIN_CORR              p_multi'  )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RECHARGE_CORR          r_multi'  ) 
    #================================================================
    # Catchment Routing
    if pm.calCatRoute():
        f.write('\n# Catchment Routing parameters'                                                          )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       TIME_CONC              t_multi'  )
        f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       TIME_TO_PEAK           t_multi'  )
    #================================================================
    # f.write('\n:SBGroupPropertyMultiplier   UpstreamOf'+Obs_NM+'       RESERVOIR_CREST_WIDTH  k_multi'      )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       MANNINGS_N             n_multi'              )
    # f.write('\n:SBGroupPropertyMultiplier   Allsubbasins       Q_REFERENCE            q_multi'              ) 
    # f.write('\n:SBGroupPropertyMultiplier   AllLakesubbasins   RESERVOIR_CREST_WIDTH  k_multi'              )
    # if observations is a lake --> calibrate individual CW
    #================================================================
    # Calibrate Lake Crest Widths
    if pm.calLakeCW():
        log.info("Lake crest widths will be calibrated.")
        if ObsType == 'RS':
            f.write('\n:SubBasinGroup   Lake_'+Obs_NM                                                            )
            f.write('\n\t'+str(SubId)                                                                            )
            f.write('\n:EndSubBasinGroup'                                                                        )    
            f.write('\n:PopulateSubBasinGroup NonLake'+Obs_NM+' With UpstreamOf'+Obs_NM+' NOTWITHIN Lake_'+Obs_NM)
            f.write('\n:SBGroupPropertyMultiplier   NonLake'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_multi'     )
            if pm.CWindv():
                log.info(Obs_NM + " lake's crest width will be calibrated individually.")
                f.write('\n:SBGroupPropertyOverride     Lake_'+Obs_NM+'          RESERVOIR_CREST_WIDTH  w_'+Obs_NM) 
            # f.write('\n:SBGroupPropertyMultiplier   Lake_'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_'+Obs_NM   ) 
        elif ObsType == 'SF' and SubId in CWList['SubBasinID'].values:
            f.write('\n:SubBasinGroup   Lake_'+Obs_NM                                                            )
            f.write('\n\t'+str(SubId)                                                                            )
            f.write('\n:EndSubBasinGroup'                                                                        )    
            f.write('\n:PopulateSubBasinGroup NonLake'+Obs_NM+' With UpstreamOf'+Obs_NM+' NOTWITHIN Lake_'+Obs_NM)
            f.write('\n:SBGroupPropertyMultiplier   NonLake'+Obs_NM+'        RESERVOIR_CREST_WIDTH  k_multi'     )
            if pm.CWindv():
                log.info("lake upstream of "+ Obs_NM + "'s lake crest width will be calibrated individually.")
                f.write('\n:SBGroupPropertyOverride     Lake_'+Obs_NM+'          RESERVOIR_CREST_WIDTH  w_'+Obs_NM) 
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
'''                                                             