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

active_diam = 984.
tp_area = np.pi * (active_diam/2.)**2  # mm^2


def Center_of_Event(sipmtable_df, sipm_thresh=0):
    event_id = sipmtable_df.event_id.values[0]
    sipmtable_df = sipmtable_df[sipmtable_df.charge > sipm_thresh]
    x = np.sum(sipmtable_df.charge*sipmtable_df.X)/np.sum(sipmtable_df.charge)
    y = np.sum(sipmtable_df.charge*sipmtable_df.Y)/np.sum(sipmtable_df.charge)
    z = np.sum(sipmtable_df.charge*sipmtable_df.Z)/np.sum(sipmtable_df.charge)
    charge = np.sum(sipmtable_df.charge)
    r = np.sqrt(x**2 + y**2)
    return pd.Series({'event_id':event_id, 'charge':charge, 'X':x, 'Y':y, 'Z':z, 'r':r})
 
def GetEres(num_files, SiPMsize, SiPMpitch, mc_name, num_sipms, event_type, rcut, zcut, sipm_thresh, outdir, outdata_dir):
    """
    Plots the energy, x, y, and z distributions of a given simulation. It also fits the energy distribution 
    and save the energy resolution to an output data directory.
    """

    coverage = 100 * num_sipms * SiPMsize**2 / tp_area
    data_dir = '/n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/eres_22072022/full_sims/'+mc_name+'/'+event_type+'/buffy/reduced_hdf5/'
    fast_sims = glob.glob(data_dir+'/*')
    num_files  = len(fast_sims)

    fast_data = pd.DataFrame()
    mc = {'size':SiPMsize, 'pitch':SiPMpitch,
        'name': f'{SiPMsize} mm size, {SiPMpitch} pitch',
        'num_sipms': num_sipms, 'coverage': coverage, 'rcut':rcut, 'sthresh':sipm_thresh}
    for j in range(0, num_files): 
        this_data = pd.read_hdf(fast_sims[j], 'SiPM/Waveforms')
        event_centers = this_data.groupby('event_id').apply(lambda grp: Center_of_Event(grp, sipm_thresh))
        event_centers = event_centers[event_centers.r < rcut]
        event_centers = event_centers[event_centers.Z < zcut]
        fast_data = fast_data.append(event_centers)

    events_list = fast_data.event_id.unique()
    bad_charge = fast_data[fast_data.charge < 100.]
    bad_z= fast_data[fast_data.Z < 150]

    plt.hist(bad_charge.charge, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Total SiPM Charge [pes]')
    plt.savefig(outdir+f'badc_charge_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_charge.X, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('X [mm]')
    plt.savefig(outdir+f'badc_x_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close() 

    plt.hist(bad_charge.Y, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Y [mm]')
    plt.savefig(outdir+f'badc_y_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_charge.r, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('R [mm]')
    plt.savefig(outdir+f'badc_r_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_charge.Z, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Z [mm]')
    plt.savefig(outdir+f'badc_z_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_z.charge, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Total SiPM Charge [pes]')
    plt.savefig(outdir+f'badz_charge_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_z.X, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('X [mm]')
    plt.savefig(outdir+f'badz_x_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close() 

    plt.hist(bad_z.Y, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Y [mm]')
    plt.savefig(outdir+f'badz_y_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_z.r, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('R [mm]')
    plt.savefig(outdir+f'badz_r_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(bad_z.Z, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Z [mm]')
    plt.savefig(outdir+f'badz_z_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()



if __name__ == '__main__':

    num_files = int(sys.argv[1])
    SiPMsize     = float(sys.argv[2])
    SiPMpitch    = float(sys.argv[3])
    mc_name      = str(sys.argv[4])
    num_sipms = int(sys.argv[5])
    event_type   = str(sys.argv[6])
    rcut         = float(sys.argv[7])
    zcut         = float(sys.argv[8])
    sipm_thresh  = int(sys.argv[9])
    outdir       =  str(sys.argv[10]) #'/n/home12/tcontreras/plots/FlexEresStudies/0vbb/'
    outdata_dir = str(sys.argv[11])
    
    GetEres(num_files, SiPMsize, SiPMpitch, mc_name, num_sipms, event_type, rcut, zcut, sipm_thresh, outdir, outdata_dir)