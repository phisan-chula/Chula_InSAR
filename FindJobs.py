#
#
#
#
import netrc,sys
import pandas as pd
import geopandas as gpd
import argparse
from hyp3_sdk import HyP3
from pathlib import Path

#########################################################################
def FindJobs( HYP3, JOB_TYPE='INSAR_GAMMA' ):
    batch = HYP3.find_jobs()
    df_job = None
    for job in batch.jobs:
        job1 =  job.to_dict().copy()
        if job1['job_type']==JOB_TYPE:
            job2 =  job1.pop('job_parameters',None).copy()
            job3 = {**job1,**job2}
            df = pd.DataFrame.from_dict( job3, orient='index' ).transpose()
            #print( df)
            if df_job is None:
                df_job = df
            else:
                df_job = pd.concat( [ df_job, df ], ignore_index=True )
            del df
        else:
            print( 'skipping ....', job1['job_type'] )
    return df_job

def PRINT_LINE():
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
