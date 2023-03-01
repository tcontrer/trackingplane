import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from fit_functions import fit_energy, plot_fit_energy2, print_fit_energy, get_fit_params
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
    return pd.Series({'event_id':event_id, 'charge':charge, 'X':x, 'Y':y, 'Z':z})

def GetCharge(num_files, SiPMsize, SiPMpitch, mc_name, event_type, rcut, zcut, sipm_thresh):
    """
    Gets the charge distribution give cuts.
    """

    data_dir = '/n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/eres_22072022/full_sims/'+mc_name+'/'+event_type+'/buffy/reduced_hdf5/'
    sims = sorted(glob.glob(data_dir+'/*'))
    num_files  = min(num_files, len(sims))

    data = pd.DataFrame()
    all_rs = pd.DataFrame()
    total_events = 0
    for j in range(0, num_files): 
        this_data = pd.read_hdf(sims[j], 'SiPM/Waveforms')
        rmax = pd.read_hdf(sims[j], 'particles/r_max').r_max
        event_centers = this_data.groupby('event_id').apply(lambda grp: Center_of_Event(grp, sipm_thresh))
        rmax.index = event_centers.event_id
        event_centers['R'] = rmax
        total_events += event_centers.count()[0]
        event_centers = event_centers[event_centers.R < rcut]
        event_centers = event_centers[event_centers.Z < zcut]

        if not event_centers.empty:
            data = data.append(event_centers)

    if data.empty:
        print('Data frame empty')
        return
    print('Num events after cut = '+str(data.count()[0])+'/'+str(total_events))

    return data
 
def GetEres(num_files, SiPMsize, SiPMpitch, mc_name, num_sipms, event_type, rcut, zcut, sipm_thresh, outdir, outdata_dir):
    """
    Plots the energy, x, y, and z distributions of a given simulation. It also fits the energy distribution 
    and save the energy resolution to an output data directory.
    """

    coverage = 100 * num_sipms * SiPMsize**2 / tp_area
    data = GetCharge(num_files, SiPMsize, SiPMpitch, mc_name, event_type, rcut, zcut, sipm_thresh)
    
    # Save dataframe
    data.to_csv(outdata_dir+'/'+mc_name+'_sthresh'+str(sipm_thresh)+'_df.csv')
    
    #####################
    ##### Eres Plot #####
    #####################
    bins_fit = 50
    if event_type == 'kr83m':
        fit_range_sipms = (np.min(data.charge), np.max(data.charge))
        plot_range = fit_range_sipms
    else:
        y, b = np.histogram(data.charge, bins= 1000, range=[np.min(data.charge), np.max(data.charge)])
        x = shift_to_bin_centers(b)
        peak = x[np.argmax(y)]
        fit_range_sipms = (peak - np.std(data.charge)/4., peak + np.std(data.charge)/4.) # only fit left half to avoid the tails
        plot_range = (peak - np.std(data.charge)/4., peak + np.std(data.charge)/4.)

    sipm_fit = fit_energy(data.charge, bins_fit, fit_range_sipms)

    mc = {'size':SiPMsize, 'pitch':SiPMpitch,'name': f'{SiPMsize} mm size, {SiPMpitch} pitch',
        'num_sipms': num_sipms, 'coverage': coverage, 'rcut':rcut, 'sthresh':sipm_thresh}
    mc['sipm_eres'], mc['sipm_fwhm'], mc['sipm_mean'], mc['sipm_eres_err'], mc['sipm_fwhm_err'], mc['sipm_mean_err'], mc['sipm_chi2'] = get_fit_params(sipm_fit)
    
    print(mc['name']+'-------------------')
    print('Coverage = '+str(mc['coverage']))
    print('Mean and std', np.mean(data.charge), np.std(data.charge))
    print('Eres err', mc['sipm_eres_err'])

    print_fit_energy(sipm_fit)

    plot_fit_energy2(sipm_fit, data.charge, plot_range)
    plt.xlabel('Charge [pes]')
    plt.title('Energy Resolution Fit, '+mc['name'])
    plt.savefig(outdir+f'eres_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(data.charge, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Total SiPM Charge [pes]')
    plt.savefig(outdir+f'charge_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(data.X, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('X [mm]')
    plt.savefig(outdir+f'x_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close() 

    plt.hist(data.Y, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Y [mm]')
    plt.savefig(outdir+f'y_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(data.R, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('R [mm]')
    plt.savefig(outdir+f'r_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    plt.hist(data.Z, bins=50, label=f'R < 300, SiPM Charge > 2')
    plt.title(mc['name']+', '+event_type)
    plt.xlabel('Z [mm]')
    plt.savefig(outdir+f'z_r{rcut}_sthresh{sipm_thresh}_'+mc_name+'.png')
    plt.close()

    # Save eres numbers to a file

    json.dump(mc, open(outdata_dir+'/'+mc_name+'.txt', 'w'))
    
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
    