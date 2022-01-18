#
#
# 1 job_find : find 1
#
#
import netrc,sys
import pandas as pd
import geopandas as gpd
import argparse
from hyp3_sdk import HyP3
from pathlib import Path
from FindJobs import *

#######################################################################
parser = argparse.ArgumentParser(description='Find job info from ASF Hyp3/GAMMA...')
parser.add_argument('-j','--job', help='job name' )
parser.add_argument('-d','--down', action='store_true',
                    help='dowload all products within job' )
args = parser.parse_args()
PRINT_LINE()
if args.job is None:
    parser.print_help()

netrc = netrc.netrc()
NODE =  'urs.earthdata.nasa.gov'
USER,_,PASSWD = netrc.authenticators( NODE )
print(f'Logging into NASA/ASF "{NODE}  User:{USER}" ...')
hyp3 = HyP3( username=USER, password=PASSWD )
print(f'Harvesting all jobs in ASF "{NODE}" ...')
print( 'Quota : ',  hyp3.my_info()['quota'] )
PRINT_LINE()
df = FindJobs( hyp3, 'INSAR_GAMMA' )
#print( 'Availble job "columns" ....\n' , df.columns )

PRINT_LINE()
print( 'Summary jobs "name" ... ')
print( df.name.value_counts() )

PRINT_LINE()
if args.job is not None:
    print( 'Job name : ', args.job )
    res = df[ df.name==args.job ].status_code.value_counts() 
    print( res )
PRINT_LINE()

if args.down and args.job is not None:
    batch = hyp3.find_jobs( status_code='SUCCEEDED', 
            name=args.job, job_type='INSAR_GAMMA' )
    #import pdb; pdb.set_trace()
    batch.download_files()

PRINT_LINE()
