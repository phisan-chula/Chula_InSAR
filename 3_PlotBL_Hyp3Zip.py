#
#
#
#
PROG='''
PlotBL_Hyp3InSAR : plot baseline network from folder of Hyp3/Gamma Zip/InSAR 
                   but extracted {GAMMA_INSAR_PRODUCT}.txt
Phisan.Chula@gmail.com ( Faculty of Engineering, Chulalongkorn University )
Intial : 15 January 2022
'''
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import datetime as dt
from collections import Counter
import sys, yaml
from PlotNetworkBL import *

############################################################
class InSAR_Baseline_Hyp3SDK( InSAR_Baseline ):
    def __init__( self, FOLDER ):
        #import pdb; pdb.set_trace()
        self.FOLDER=FOLDER
        df_ifg = pd.DataFrame( FOLDER.glob( '*.txt'), columns=['Hyp3Path'] )
        df_ifg[['NAME4', 'dt_master','dt_slave', 'scene_master','scene_slave',
                 'Bperp_m', 'Btemp_d' ] ] = df_ifg.apply( self.ParseIfgProduct , 
                         axis='columns', result_type='expand' )
        ####################################
        grs = list( set( list(df_ifg.scene_master)+list(df_ifg.scene_slave)) )
        df_ref = pd.DataFrame( grs , columns=['Granule'] )
        df_ref['NAME4'] = df_ref.Granule.str[-4:]
        def ParseGranule(row):
            S1,_,_,_,_,dtacq,_,_,_,NAME4 = row.Granule.split('_') 
            return dt.datetime.strptime( dtacq, '%Y%m%dT%H%M%S' )
        df_ref['dtAcq']  = df_ref.apply( ParseGranule , axis='columns' )
        df_ref.sort_values(by='dtAcq',ascending=False,inplace=True,ignore_index=True)
        #import pdb; pdb.set_trace()
        df_ref['Btemp0_d']  = (df_ref['dtAcq']-df_ref.iloc[0]['dtAcq']).dt.days
        self.df_ifg = df_ifg; self.df_ref = df_ref
        self.SolveBaselineRef()
        super().__init__()

    def ParseIfgProduct(self, row):
        S1,dtms,dtsl,VVP,_,_,_,NAME4 = row['Hyp3Path'].stem.split('_')
        day_sep = int(VVP[-3:])   # only + !!!
        dtms = dt.datetime.strptime( dtms, '%Y%m%dT%H%M%S' )
        dtsl = dt.datetime.strptime( dtsl, '%Y%m%dT%H%M%S' )
        day_diff =  (dtsl-dtms).days
        with open( row.Hyp3Path ) as f:
            YAML = yaml.load( f, Loader=yaml.FullLoader )
        return (NAME4, dtms, dtsl, YAML['Reference Granule'], YAML['Secondary Granule'],
                YAML['Baseline'],  day_diff )

    def SolveBaselineRef(self):
        N = len(self.df_ref)
        mtx = list(); rhs = list()
        mtxrow = N*[0];  mtxrow[0]=+1; mtx.append( mtxrow ) # latest acq - reference
        rhs.append( 0.0 )  # refence ganule
        for i,row in self.df_ifg.iterrows():
            mtxrow = N*[0]
            idx_fr = self.df_ref[ self.df_ref['Granule']==row.scene_master ].index[0]
            idx_to = self.df_ref[ self.df_ref['Granule']==row.scene_slave ].index[0]
            mtxrow[idx_fr] = -1
            mtxrow[idx_to] = +1
            mtx.append( mtxrow )
            rhs.append( row.Bperp_m )
            #print( mtxrow )
        A = np.array(mtx)
        B = np.array(rhs).T
        res = np.linalg.lstsq(A,B,rcond=-1)
        if res[1]>1: raise f"Waning residual {res[1]} is too large !!!!"
        self.df_ref['Bperp0_m'] = np.round( res[0], 1)
        #import pdb; pdb.set_trace()
        return

############################################################
#FOLDER = Path( 'Prepare/ASC_CMI_PYO_2021' )
FOLDER = Path( 'Prepare/DES_CMI_PYO_2021' )

if len(sys.argv)==2:
    FOLDER = sys.argv[1]
    bl = InSAR_Baseline_Hyp3SDK( Path(FOLDER) )
else:
    print(PROG)
    print('Usage: PlotBL_InSAR <DIR_OF_IFGs')
    exit(-1)

df_ref, df_ifg = bl.CalcBaseLine()
print('Plotting baseline network and histogram ...')
bl.PlotBaseline()
bl.PlotHisto()
#import pdb; pdb.set_trace()
