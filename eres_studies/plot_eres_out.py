import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

mcs = {'s1.3mmp3.5mm':
        {'size':1.3, 'pitch':3.5,  'teflon':False, 'nsipms':61053, 'range':(2.15e6,2.25e6), 'kr_range':(17000,25000),  'run':True},
    's1.3mmp2.4mm':
        {'size':1.3, 'pitch':2.4,    'teflon':False, 'nsipms':129889, 'range':(4.6e6,4.8e6), 'kr_range':(39000,85000), 'run':True},
    's3mmp5.5mm':
        {'size':3, 'pitch':5.5,  'teflon':False, 'nsipms':24748, 'range':(5.8e6,6.5e6), 'kr_range':(39000,85000),'run':False}}

# RunEres 
event_type = 'kr83m'
rcut = 300. # mm
zcut = 1200. # mm
sthresholds = [0,3,6,7] # pes
outdir = f'/n/home12/tcontreras/plots/FlexEresStudies/{event_type}/'
inputdir = 'data_eres_'+event_type+f'_rcut{rcut}_zcut{zcut}/'

bins = 100
this_range = 'range'
if event_type == 'kr83m':
    this_range = 'kr_range'
for name in mcs:
    if mcs[name]['run']:
        for sthresh in sthresholds:
            data = pd.read_csv(inputdir+name+'_sthresh'+str(sthresh)+'_df.csv')
            print(data.charge)
            plt.hist(data.charge.to_list(), range=mcs[name][this_range], bins=bins, label='sthresh = '+str(sthresh), histtype='step')
        plt.xlabel('charge [pes]')
        plt.title(name+', '+event_type+', R < '+str(rcut)+' mm, z < '+str(zcut)+' mm')
        plt.legend()
        plt.savefig(outdir + name + '_all_sthresh_charge.png')
        plt.close()