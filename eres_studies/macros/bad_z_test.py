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

num_files = 1
event_type   = '0vbb'
SiPMsize     = 1.3
SiPMpitch    = 2.4
mc_name      = 's'+str(SiPMsize)+'mmp'+str(SiPMpitch)+'mm'
rcut         = 300
zcut         = 1200
sipm_thresh  = 2
outdir       =  '/n/home12/tcontreras/plots/FlexEresStudies/0vbb/'

df = pd.DataFrame()
mc = {'size':SiPMsize, 'pitch':SiPMpitch,
    'name': f'{SiPMsize} mm size, {SiPMpitch} pitch',
    'rcut':rcut, 'sthresh':sipm_thresh}

def Center_of_Event(sipmtable_df, sipm_thresh=0):
    event_id = sipmtable_df.event_id.values[0]
    sipmtable_df = sipmtable_df[sipmtable_df.charge > sipm_thresh]
    x = np.sum(sipmtable_df.charge*sipmtable_df.X)/np.sum(sipmtable_df.charge)
    y = np.sum(sipmtable_df.charge*sipmtable_df.Y)/np.sum(sipmtable_df.charge)
    z = np.sum(sipmtable_df.charge*sipmtable_df.Z)/np.sum(sipmtable_df.charge)
    charge = np.sum(sipmtable_df.charge)
    r = np.sqrt(x**2 + y**2)
    return pd.Series({'event_id':event_id, 'charge':charge, 'X':x, 'Y':y, 'Z':z, 'r':r})

for j in range(0, num_files): 
    this_data = pd.read_hdf(fast_sims[j], 'SiPM/Waveforms')

    print('Raw Z',this_data.Z.to_list())
    print('Mean raw z', this_data.groupby('event_id').apply(lambda grp: grp.Z.mean()).to_list())

    event_centers = this_data.groupby('event_id').apply(lambda grp: Center_of_Event(grp, sipm_thresh))
    print('Center Z', event_centers.Z)
    #event_centers = event_centers[event_centers.r < rcut]
    #event_centers = event_centers[event_centers.Z < zcut]
    #df = fast_data.append(event_centers)