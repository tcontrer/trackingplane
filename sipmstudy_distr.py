"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the energy distribution of each simulated
detector configuration.
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
nfiles = 1 # will fail if too few events
local = True
event_type = 'kr'
teflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:

    sipms = pd.DataFrame()
    pmts = pd.DataFrame()
    for file in mc['files']:
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

        # Sum up all charges per event in pmts
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        pmt_response_byevent = pmt_response.groupby('event_id')
        charges = pmt_response_byevent.agg({"charge":"sum"})
        pmts = pmts.append(charges)


    mc['sipms'] = sipms[sipms.charge>0]
    mc['pmts'] = pmts[pmts.charge>0]
    if mc['size'] == 6:
        print(sipms[sipms.charge < 10000].mean)

if event_type == 'kr':
    sipm_range = (0, 400000)
    pmt_range = (0, 10000)
else:
    sipm_range = (0, 21000000)
    pmt_range = (0, 600000)


for mc in mcs:
    plt.hist(mc['sipms'].charge, label='sipms', bins=100)
    plt.xlabel("Charge per event in SiPMS [pes]")
    plt.title("NEXT-100, "+mc['name'])
    plt.legend()
    plt.savefig(outdir+'distr_'+'sipms_energy_'+mc['dir']+str(mc['size'])+'.png')
    plt.close()

for mc in mcs:
    plt.hist(mc['pmts'].charge, label='pmts', bins=100)
    plt.xlabel("Charge per event in PMTs [pes]")
    plt.title("NEXT-100, "+mc['name'])
    plt.legend()
    plt.savefig(outdir+'distr_'+'pmts_energy_'+mc['dir']+str(mc['size'])+'.png')
    plt.close()

for mc in mcs:
    plt.hist(mc['sipms'].charge, label=mc['name'], bins=100, range=sipm_range)
plt.xlabel("Charge per event in SiPMs [pes]")
plt.title("NEXT-100")
plt.legend()
plt.savefig(outdir+'distr_'+'sipm_energy_comp.png')
plt.close()

for mc in mcs:
    plt.hist(mc['pmts'].charge, label=mc['name'], bins=100, range=pmt_range)
plt.xlabel("Charge per event in PMTs [pes]")
plt.title("NEXT-100")
plt.legend()
plt.savefig(outdir+'distr_'+'pmt_energy_comp.png')
plt.close()
