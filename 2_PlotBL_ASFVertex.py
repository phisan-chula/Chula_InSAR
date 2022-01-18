#
#
PROG='''
PlotBL_ASFVertex : plot baseline network from ASF Veter Web interface
               via file asf-sbas-pairs.csv
Phisan.Chula@gmail.com ( Faculty of Engineering, Chulalongkorn University )
Hisotry : 20 Dec 2021  initial
          15 Jan 2022  refractoring...
'''
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import datetime as dt
from collections import Counter
import sys
from PlotNetworkBL import *

pd.set_option('display.max_colwidth', None)
##################################################################
class InSAR_Baseline_ASFVertex( InSAR_Baseline ):
    ''' read ASF Vertex  asf-sbas-pairs.csv resulted from ASF 
        Vertext application '''
    def __init__(self, FOLDER):
        self.FOLDER = FOLDER
        FILE = Path(FOLDER).joinpath('asf-sbas-pairs.csv')
        df_csv = pd.read_csv( FILE , skipinitialspace=True )
        ifgs = list() ; refs = list()
        for i,row in df_csv.iterrows():
            #import pdb; pdb.set_trace()
            dtms = row.Reference.split('_')[5] 
            dtsl = row.Secondary.split('_')[5]
            dt_ms = dt.datetime.strptime( dtms, '%Y%m%dT%H%M%S' )
            dt_sl = dt.datetime.strptime( dtsl, '%Y%m%dT%H%M%S' )
            bl0_ms = row['Reference Perpendicular Baseline (meters)']
            bl0_sl = row['Secondary Perpendicular Baseline (meters)']
            bperp = bl0_sl-bl0_ms
            btemp = row['Pair Temporal Baseline (days)']
            ifgs.append( [ dt_ms, dt_sl, bperp, btemp, 
                           row['Reference'], row['Secondary']  ] )
            refs.append( [ row['Reference'], dt_ms, bl0_ms ] )
            refs.append( [ row['Secondary'], dt_sl, bl0_sl ] )
        df_ifg = pd.DataFrame( ifgs, columns=['dt_master', 'dt_slave',
            'Bperp_m', 'Btemp_d', 'scene_master', 'scene_slave' ] )
        ###################################################
        df_ref = pd.DataFrame( refs, columns=['Granule', 'dtAcq', 'Bperp0_m' ] )
        df_ref.sort_values( by='dtAcq', ascending=False, inplace=True, ignore_index=True)
        df_ref.drop_duplicates( inplace=True,ignore_index=True )
        df_ref['PROD'] = df_ref['Granule'].str[-4:]
        df_ref['Btemp0_d'] = df_ref['dtAcq']-df_ref.iloc[0]['dtAcq']
        df_ref['Btemp0_d'] = df_ref['Btemp0_d'].dt.days
        ###################################################
        self.df_ifg = df_ifg
        self.df_ref = df_ref
        self.df_csv = df_csv
        super().__init__()

############################################################
############################################################
############################################################
if __name__=="__main__":
    if len(sys.argv)==2:
        FOLDER = sys.argv[1]
        bl = InSAR_Baseline_ASFVertex( FOLDER )
    else:
        print(PROG)
        print('Usage: PlotBL_InSAR DIR_OF_IFGs')
        exit(-1)
    ############################################################
    DIR_NAME = Path(FOLDER).resolve().stem
    df_ref,df_ifg = bl.CalcBaseLine()
    print('Plotting baseline network and histogram ...')
    bl.PlotBaseline( )
    bl.PlotHisto()
    #############################
    if 0:
        print('@@@@@@@@@ P R O C E S S I N G   S P E C I A L   F E A T U R E @@@@@@@@@')
        print('Partition IFGs for Boat/LookMee/PSN')
        for YEAR,TEAM in [(2019,'BOAT'),(2020,'LKMEE') ,(2021,'PSN')]:
            df_ifg_part =  df_ifg[df_ifg.dt_master.dt.year==YEAR]
            df_csv_part =  bl.df_csv.loc[df_ifg_part.index]
            print( f'Year {YEAR}   Team : {TEAM}    Number of scene : {len(df_csv_part)} ' )
            ORB = Path(FOLDER).stem[:3]
            out_csv = Path(FOLDER, f'sbas-pair-{ORB}-{YEAR}.csv' )
            df_csv_part.to_csv( out_csv, index=False )

#import pdb ; pdb.set_trace()


