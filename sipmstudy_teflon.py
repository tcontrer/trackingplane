"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and compare the energy distribution of each simulated
detector configuration with and without teflon.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm
from open_files import make_mc_dictionaries

from ic_functions import *

print("Starting")
nfiles = 100 # will fail if too few events
local = False
event_type = 'kr'
tp_area = np.pi * (984./2.)**2 # mm^2      

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs_teflon, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon=True)
print([mc['teflon'] for mc in mcs_teflon])
mcs_noteflon, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon=False)
print([mc['teflon'] for mc in mcs_teflon])

def fill_mcs(mcs):
    for mc in mcs:
        sipms = pd.DataFrame()
        pmts = pd.DataFrame()
        for file in mc['files']:
            print(file)
            try:
                sns_response = pd.read_hdf(file, 'MC/sns_response')
            except:
                print("Couldn't open file: "+file)
                continue

            sns_response_sorted = sns_response.sort_values(by=['sensor_id'])

            # Sum up all charges per event in sipms
            sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
            sipm_response_byevent = sipm_response.groupby('event_id')
            charges = sipm_response_byevent.agg({"charge":"sum"})
            sipms = sipms.append(charges)

        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]
        mc['sipms'] = sipms[sipms.charge>0]
        mc['coverage'] = 100. * len(sipm_positions) * mc['size']**2 / tp_area
    return mcs

mcs_teflon = fill_mcs(mcs_teflon)
mcs_noteflon = fill_mcs(mcs_noteflon)

if event_type == 'kr':
    sipm_range = (0, 400000)
    pmt_range = (0, 10000)
else:
    sipm_range = (0, 21000000)
    pmt_range = (0, 600000)

for mc, mc_nt in zip(mcs_teflon, mcs_noteflon):
    plt.hist(mc['sipms'].charge, label='teflon', bins=100)
    plt.hist(mc_nt['sipms'].charge, label='no teflon', bins=100)
    plt.xlabel("Charge per event in SiPMS [pes]")
    plt.title("NEXT-100, "+mc['name'])
    plt.legend()
    plt.savefig(outdir+'teflon_'+'sipms_energy_'+mc['dir']+str(mc['size'])+'.png')
    plt.close()

mcs_by_size = [[],[],[]]
mcs_by_size_nt = [[],[],[]]
for mc, mc_nt in zip(mcs_teflon, mcs_noteflon):
    if mc['size'] == 1.3:
        mcs_by_size[0].append(mc)
        mcs_by_size_nt[0].append(mc_nt)
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
        mcs_by_size_nt[1].append(mc_nt)
    if mc['size'] == 6:
        mcs_by_size[2].append(mc)
        mcs_by_size_nt[2].append(mc_nt)

for size, size_nt in zip(mcs_by_size, mcs_by_size_nt):
    means = [np.mean(mc['sipms'].charge) for mc in size]
    means_noteflon =[np.mean(mc['sipms'].charge) for mc in size_nt]
    coverages = [mc['coverage'] for mc in size]
    div = np.array(means) / np.array(means_noteflon)

    plt.plot(coverages, div, 'o', label=str(size[0]['size'])+'mm SiPMs')
plt.xlabel('Coverage (%)')
plt.ylabel('mean teflon / no teflon charge')
plt.legend()
plt.savefig(outdir+'teflon_div_comp.png')
plt.close()
