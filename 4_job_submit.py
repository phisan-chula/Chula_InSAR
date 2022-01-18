#
#
PROG = '''
4_job_submit : submit pair(s) of S1A/S1B InSAR to ASF Vertex processing
                system via Hyp3 SDK
 Author       : Phisan Santitamnont (phisan.chula@gmail.com)
 History 18 Mar 2022 : Initial
'''
#
#
import json
import netrc,sys
import pandas as pd
import geopandas as gpd
from hyp3_sdk import HyP3
import asf_search as asf
from pathlib import Path


print(80*'-')
print(PROG)
print(80*'-')
netrc = netrc.netrc()
NODE =  'urs.earthdata.nasa.gov'
USER,_,PASSWD = netrc.authenticators( NODE )
print(f'Logging into NASA/ASF "{NODE}  User:{USER}" ...')
hyp3 = HyP3( username=USER, password=PASSWD )
print(f'Harvesting all jobs in ASF "{NODE}" ...')
print(  hyp3.my_info() )
print(80*'-')

MS = 'S1A_IW_SLC__1SDV_20211227T113031_20211227T113059_041194_04E525_14FD'
# BL = -82m -120d
SL = 'S1A_IW_SLC__1SDV_20210829T113032_20210829T113100_039444_04A8F0_A17C'
OPTS = dicts( include_los_displacement=True,  
                include_inc_map=True,
                looks='20x4', 
                include_dem=True,  
                include_wrapped_phase=True,
                apply_water_mask=True,
                include_displacement_maps=True )
if 1:
    result = hyp3.prepare_insar_job( MS, SL, name='TestInSAR', **OPTS ) 
    print( result )
    result = hyp3.submit_insar_job( MS, SL, name='TestInSAR', **OPTS )
    print( result )
    import pdb; pdb.set_trace()
