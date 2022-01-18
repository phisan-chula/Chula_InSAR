#
#
'''
PlotBL_InSAR : plot baseline network from UK-COMET LiCSBAS or ASF3 HyP3 
               GAMMA structure
Phisan.Chula@gmail.com ( Faculty of Engineering, Chulalongkorn University )
Intial : 20 Dec 2021
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

####################################################################
class InSAR_Baseline:
    '''
    self.df_ref.info()
     0   Granule   29 non-null     object
     2   dtAcq     29 non-null     datetime64[ns]
     3   Btemp0_d  29 non-null     int64
     4   Bperp0_m  29 non-null     float64
     5   MMDD      29 non-null     object
     self.df_ifg.info()
     0   Hyp3Path      100 non-null    object        
     1   Name4         100 non-null    object        
     2   dt_master     100 non-null    datetime64[ns]
     3   dt_slave      100 non-null    datetime64[ns]
     4   scene_master  100 non-null    object        
     5   scene_slave   100 non-null    object        
     6   Bperp_m       100 non-null    float64       
     7   Btemp_d       100 non-null    int64         
     8   pnt_master    100 non-null    object        
     9   pnt_slave     100 non-null    object        
    '''
    def __init__(self):
        print('class InSAR_Baseline:')
        DIR_NAME = Path(self.FOLDER).resolve().stem
        RANGE = (self.df_ref.dtAcq.max()-self.df_ref.dtAcq.min()).days
        self.TITLE = 'SBAS:{} | Bperp:{}/{}m Btemp:{}d | Days:{} Granules:{} IFGs: {}'.\
             format( DIR_NAME, self.df_ifg['Bperp_m'].max(),self.df_ifg['Bperp_m'].min(),
                self.df_ifg['Btemp_d'].max(), RANGE, len(self.df_ref), len(self.df_ifg) )
        print( self.TITLE )

    def CalcBaseLine( self ):
        df_ifg = self.df_ifg
        df_ref = self.df_ref
        df_ifg['dt_master'] = pd.to_datetime( df_ifg['dt_master'] )
        df_ifg['dt_slave'] = pd.to_datetime( df_ifg['dt_slave'] )
        coords = list(); BLs = list()
        for i,row in df_ifg.iterrows():
            idx_ms = df_ref[ df_ref.dtAcq==row.dt_master ].iloc[0]
            idx_sl = df_ref[ df_ref.dtAcq==row.dt_slave  ].iloc[0]
            coords.append( [ (idx_ms.Btemp0_d,idx_ms.Bperp0_m),
                             (idx_sl.Btemp0_d,idx_sl.Bperp0_m) ]  )
            BLs.append( idx_sl.Bperp0_m - idx_ms.Bperp0_m ) 
        df_ifg[ ['pnt_master','pnt_slave' ]] =  pd.DataFrame( coords )
        df_ifg['Btemp_d'] = (df_ifg['dt_slave']-df_ifg['dt_master']).dt.days
        df_ifg['Bperp_m'] = BLs
        return df_ref, df_ifg

    def PlotBaseline( self ):
        def toMMDD(dt ):
            return '{:02d}/{:02d}'.format( dt.month, dt.day )
        self.df_ref['MMDD'] = self.df_ref['dtAcq'].apply( toMMDD )
        RANGE = (self.df_ref.dtAcq.max()-self.df_ref.dtAcq.min()).days
        fig,ax = plt.subplots(1,1, figsize=(20*RANGE/365,10))
        ax2 = ax.twiny()
        ax2.set_xlim( self.df_ref.iloc[-1].Btemp0_d, self.df_ref.iloc[0].Btemp0_d)
        ax2.set_xlabel('Days from Reference')
        for i, row in self.df_ref.iterrows():
            ax.annotate(f'{row.MMDD}<{row.PROD}>',( row.dtAcq, row.Bperp0_m ),
                family='sans-serif', fontsize=12, color='darkslategrey', ha='center')
        for i,row in self.df_ifg.iterrows():
            ax.plot( [row.dt_master, row.dt_slave] , 
                     [row.pnt_master[1], row.pnt_slave[1]]  )
            if 'PROD' in self.df_ifg.columns:
                mid_dt = row.dt_master + (row.dt_slave-row.dt_master)/2.
                mid_bl = (row.pnt_master[1]+row.pnt_slave[1] )/2.
                ax.text( mid_dt,mid_bl, row['PROD'], c='red', alpha=0.5 )
        ax.annotate('Ref.Granule', xy=(self.df_ref.iloc[0].dtAcq,0), xytext=(0,-50),
            textcoords='offset points',arrowprops=dict(facecolor='black', shrink=0.05),)
        self.df_ref.plot.scatter(x='dtAcq',y='Bperp0_m',s=10,c='r',ax=ax)
        ax.xaxis.set_major_locator( mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter( mdates.DateFormatter('%d-%m-%Y') )
        DAYS_LEAD = dt.timedelta( days=20 )
        ax.set_xlim(  self.df_ref.iloc[-1].dtAcq-DAYS_LEAD, 
                      self.df_ref.iloc[ 0].dtAcq+DAYS_LEAD )
        ax.tick_params(axis='x', labelrotation=90)
        ax.set_xlabel('Date')
        plt.suptitle( self.TITLE )
        plt.tight_layout()
        ax.grid( visible=True, which='major', axis='both' )
        plt.savefig('BaselineNetwork.png')
        plt.savefig('BaselineNetwork.pdf')
        #plt.show()

    def PlotHisto( self ):
        #import pdb; pdb.set_trace()
        fig,axs = plt.subplots(1,2, figsize=(20,5))
        self.df_ifg['Bperp_m'].plot.hist(ax=axs[0], alpha=0.6, bins=10)
        axs[0].set_title( f'Perpendicular Baseline' )
        axs[0].set_xlabel('meter')
        self.df_ifg['Btemp_d'].plot.hist(ax=axs[1], alpha=0.6, bins=10)
        axs[1].set_title( f'Temporal Baseline' )
        axs[1].set_xlabel('days')
        plt.suptitle( self.TITLE )
        fig.tight_layout()
        plt.savefig('BaselineHistogr.png')
        #plt.show()
    
##################################################################
class InSAR_Baseline_LiCSBAS( InSAR_Baseline ):
    def __init__(self, LiCSAR_FOLDER ):
        IFG_PATH = Path(LiCSAR_FOLDER).joinpath('interferograms')
        BSL_PATH = Path(LiCSAR_FOLDER).joinpath('metadata/baselines')
        self.df_ref = pd.read_csv( BSL_PATH, 
                sep=' ', header=None, parse_dates=[0,1],
                         names=['dtRef','dtGranule','Bperp0_m', 'Btemp0_d'] ) 
        #############################    
        pairs = Path( IFG_PATH).glob('./*')
        ifgs = list()
        for i in pairs:
            ifgs.append( i.stem.split('_') )
        self.df_ifg = pd.DataFrame( ifgs, columns=['master','slave'] )
        pass

def ViewUnwrapProduct():
    import os
    df_hi = df_ifg[ df_ifg.Btemp_d<10  ].iloc[0:2]
    df_lo = df_ifg[ df_ifg.Btemp_d>200 ].iloc[0:2]
    df_hilo = pd.concat( [ df_hi,df_lo]  )
    for i,row in df_hilo.iterrows():
        ma_sl = '{}_{}'.format(  row.master.strftime('%Y%m%d') , 
                                 row.slave.strftime('%Y%m%d')     )
        png  =  '{}/{}/{}.geo.unw.png'.format( IFG_PATH, ma_sl, ma_sl )  
        print( '{} {} days'.format( ma_sl, row.Btemp_d ) )
        os.system( f'eog  {png} &')

############################################################
############################################################
############################################################
if __name__=="__main__":
    if 0:
        FOLDER = 'Prepare' # expect asf-sbas-pairs.csv
        bl = InSAR_Baseline_ASFHyP3( FOLDER )

    if len(sys.argv)==2:
        FOLDER = sys.argv[1]
        bl = InSAR_Baseline_ASFHyP3( FOLDER )
    else:
        print(PROG)
        print('Usage: PlotBL_InSAR <DIR_OF_IFGs')
        exit(-1)

    ############################################################
    DIR_NAME = Path(FOLDER).resolve().stem
    df_ref,df_ifg = bl.CalcBaseLine()
    print( df_ifg['Bperp_m'].describe() )
    print( df_ifg['Btemp_d'].describe() )
    #############################    
    edge_cnt = list()
    for node in ('master','slave'):
        for i,grp in df_ifg.groupby(node):
            if len(grp)>12:
                print( i,grp )
            edge_cnt.append( len(grp) )
        print( f'from "{node}" to its pairs count :  ' )
        print( Counter(edge_cnt).most_common() )

    print('Total interferograms : {:,} products'.format( len(df_ifg) ) )
    #############################
    if 1:
        print('Plotting baseline network and histogram ...')
        bl.PlotBaseline(TITLE)
        bl.PlotHisto(TITLE)
    #ViewUnwrapProduct()

    #############################
    if 0:
        print('Partition IFGs for Boat/LookMee/Latae')
        for YEAR,TEAM in [(2019,'BOAT'),(2020,'LKMEE') ,(2021,'PSN')]:
            df_part =  df_ifg[df_ifg.master.dt.year==YEAR]
            print( f'Year {YEAR}   Team : {TEAM}    Number of scene : {len(df_part)} ' )
        #import pdb; pdb.set_trace()

