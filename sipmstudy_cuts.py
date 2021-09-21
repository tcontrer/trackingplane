"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the energy resolution of the simulations
detector configuration.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from open_files import make_mc_dictionaries

from ic_functions import *

print("Starting")
nfiles = 10 # will fail if too few events
local = False
event_type = 'kr'
teflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

cuts = [i for i in range(0,50)]
for mc in mcs:
    sipm_response = pd.DataFrame()
    #eff = {cut:pd.DataFrame() for cut in cuts}
    for file in mc['files']:
        print('Running over: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])

        # Sum up all charges per event in sipms
        sipm_response = sipm_response.append(sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999])

    this = sipm_response.groupby('event_id')
    total_charges = this.agg({"charge":"sum"})

    efficiencies = []
    for cut in cuts:
        cut_sipm_response = sipm_response[sipm_response.charge > cut]
        this = cut_sipm_response.groupby('event_id')
        charges = this.agg({"charge":"sum"})
        eff = charges/total_charges
        efficiencies.append(eff.charge.mean())# Calculate efficiencies based on threshold cut

    mc['eff'] = efficiencies
    mc['sipms'] = sipm_response

if event_type == 'kr':
    event_str = '41.5 keV'
else:
    event_str = r'$Q_{\beta \beta}$'

for mc in mcs:
    plt.hist(mc['sipms'].groupby('event_id').apply(lambda grp: grp.groupby('sensor_id').agg({'charge':'sum'})).charge)
    plt.title('Signal per SiPM per event')
    plt.xlabel('charge [pes]')
    plt.yscale('log')
    plt.savefig(outdir+'cuts_charge.png')
    plt.close()


mcs_by_size = [[], [], []]
for mc in mcs:
    r = (0,100)
    b = 100
    if mc['size'] == 1:
        mcs_by_size[0].append(mc)
        mc['r'] = (0,20)
        mc['b'] = 20
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
        mc['r'] = (0,100)
        mc['b'] = 100
    elif mc['size'] == 6:
        mcs_by_size[2].append(mc)
        mc['r'] = (0,500)
        mc['b'] = 500

for mcs in mcs_by_size:

    for mc in mcs:
        plt.hist(mc['sipms'].groupby('event_id').apply(lambda grp: grp.groupby('sensor_id').agg({'charge':'sum'})).charge, bins=mc['b'], range=mc['r'])
        plt.title('Signal per SiPM per event')
        plt.xlabel('charge [pes]')
        plt.yscale('log')
        plt.savefig(outdir+'cuts_charge_'+mc['name']+'.png')
        plt.close()

    for mc in mcs:
        plt.hist(mc['sipms'].groupby('event_id').apply(lambda grp: grp.groupby('sensor_id').agg({'charge':'sum'})).charge, bins=mc['b'], range=mc['r'], label=mc['name'])
    plt.title('Signal per SiPM per event')
    plt.xlabel('charge [pes]')
    plt.legend()
    plt.savefig(outdir+'cuts_charge'+str(mc['size'])+'.png')
    plt.close()

    for mc in mcs:
        print(mc['name']+' eff: ', mc['eff'])
        plt.plot(cuts, mc['eff'], 'o', label=mc['name'])
    plt.xlabel('SiPM signal threshold [pes]')
    plt.ylabel('Signal after threshold / total signal')
    plt.title('SiPM Efficiency, '+event_str)
    plt.legend()
    plt.savefig(outdir+'cuts_eff_'+str(mc['size'])+'.png')
    plt.close()

    for mc in mcs:
        plt.plot(cuts, mc['eff'], 'o')
        plt.xlabel('SiPM signal threshold [pes]')
        plt.ylabel('Signal after threshold / total signal')
        plt.title('SiPM Efficiency, '+mc['name'])
        plt.savefig(outdir+'cuts_eff_'+mc['name']+'.png')
        plt.close()
