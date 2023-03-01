import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from fit_functions import fit_energy, plot_fit_energy, print_fit_energy, get_fit_params
from ic_functions import *
from invisible_cities.core.core_functions  import shift_to_bin_centers
import invisible_cities.database.load_db as db
import json
import glob
import sys


def MakePlots(mc_name, event_type, outdir):

    data_dir = '/n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/eres_22072022/full_sims/'+mc_name+'/'+event_type+'/nexus/hdf5/'
    files = glob.glob(data_dir+'/*')
    num_files  = len(files)

    configs = []
    for j in range(0, num_files):
        try:
            len_config = pd.read_hdf(files[j], 'MC/configuration').count()[0] 
            configs.append(len_config)
        except:
            print('Could not open files: '+files[j])
    print(configs)
    plt.hist(configs)
    plt.title(mc_name+', '+event_type)
    plt.xlabel('length of config')
    plt.savefig(outdir+f'nexus_config_'+mc_name+'.png')
    plt.close() 

    """
    hits = pd.DataFrame()
    for j in range(0, num_files): 
        these_hits = pd.read_hdf(files[j], 'MC/hits') 
        hits = hits.append(these_hits)
    
    plt.hist(hits.x)
    plt.title(mc_name+', '+event_type)
    plt.xlabel('x')
    plt.savefig(outdir+f'nexus_x_'+mc_name+'.png')
    plt.close() 

    plt.hist(hits.y)
    plt.title(mc_name+', '+event_type)
    plt.xlabel('y')
    plt.savefig(outdir+f'nexus_y_'+mc_name+'.png')
    plt.close() 

    plt.hist(hits.z)
    plt.title(mc_name+', '+event_type)
    plt.xlabel('z')
    plt.savefig(outdir+f'nexus_z_'+mc_name+'.png')
    plt.close() 

    plt.hist(s13mmp24mm_sns_response.groupby('event_id').apply(lambda grp: grp.charge.sum()), label='s1.3mmp2.4mm nexus')

    return
    plt.xlabel('Sensor Response charge [pes]')
    plt.title(mc_name+', '+event_type)
    plt.savefig(outdir+f'nexus_charge_'+mc_name+'.png')
    plt.close()
    """

if __name__ == '__main__':

    mc_name      = str(sys.argv[1])
    event_type   = str(sys.argv[2])
    outdir       =  str(sys.argv[3]) #'/n/home12/tcontreras/plots/FlexEresStudies/0vbb/'
    
    MakePlots(mc_name, event_type, outdir)