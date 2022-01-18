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
import argparse

#######################################################################
MS = 'S1A_IW_SLC__1SDV_20211227T113031_20211227T113059_041194_04E525_14FD'
# BL = -82m -120d
SL = 'S1A_IW_SLC__1SDV_20210829T113032_20210829T113100_039444_04A8F0_A17C'

parser = argparse.ArgumentParser(
        description='Submit job to ASF Vertext for InSAR Processing...')
parser.add_argument('-j','--job', help='job name, will be created if not any' )
parser.add_argument('-p','--pair', help='pair of granules to be processed (NAME4:NAME4)' )
parser.add_argument('-x','--execute', action='store_true', help='do execution the job' )
#args = parser.parse_args([ '-j', 'new_job', '-p', f'{MS}:{SL}' ])
args = parser.parse_args()
if args.job is None or args.pair is None:
    parser.print_help()
    exit(-1)
#import pdb; pdb.set_trace()
MS,SL = args.pair.split(':')
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

OPTS = dict( include_los_displacement=True,  
                include_inc_map=True,
                looks='20x4', 
                include_dem=True,  
                include_wrapped_phase=True,
                #apply_water_mask=True,
                #include_displacement_maps=True ,
                )
if 1:
    print('*** dry run no actual submitting ...***')
    result = hyp3.prepare_insar_job( MS, SL, name='MorePairs', **OPTS ) 
    print( result )
if args.execute:
    print('*** do submitting ...***')
    result = hyp3.submit_insar_job( MS, SL, name='MorePairs', **OPTS )
    print( result )
print('@@@@@@@ end of 4_job_submit @@@@@@@@@' )
#import pdb; pdb.set_trace()
