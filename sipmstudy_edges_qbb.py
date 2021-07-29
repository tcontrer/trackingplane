"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the number of photons seen by the SiPMs, ranking
the SiPMs by the ammount of photons it sees.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

print("Starting")
nfiles = 1000 # will fail if too few events
local = False
event_type = 'qbb'
pteflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:
    sipms_mean = np.array([])
    sipms_max = np.array([])
    for file in mc['files']:

        print('Running: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        # Sort to sum up all charges for each sipms
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        sipms_mean = np.append(sipms_mean, sipm_response.groupby('event_id').apply(lambda grp: np.mean(grp.charge)))
        sipms_max = np.append(sipms_max, sipm_response.groupby('event_id').apply(lambda grp: np.max(grp.charge)))

    mc['sipms_mean'] = sipms_mean
    mc['sipms_max'] = sipms_max

mcs_by_size = [[], [], []]
for mc in mcs:
    if mc['size'] == 1:
        mcs_by_size[0].append(mc)
        mc['r_max'] = (0,1500)
        mc['r_mean'] = (0,8)
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
        mc['r_max'] = (0, 10000)
        mc['r_mean'] = (0,25)
    elif mc['size'] == 6:
        mcs_by_size[2].append(mc)
        mc['r_max'] = (0, 35000)
        mc['r_mean'] = (0,60)

bins = 100
for mcs in mcs_by_size:
    bins_mean = 0
    for mc in mcs:
        plt.hist(sipms_max, label=mc['name'], range=mc['r_max'], bins=bins)
        bins_mean = max(bins_mean, mc['r_mean'][1])
    plt.xlabel('max charge [pes] / microsecond / event')
    plt.title(str(mc['size'])+'mm SiPMs')
    plt.yscale('log')
    plt.legend()
    plt.savefig(outdir+'edges_max_'+str(mc['size'])+'mm.png')
    plt.close()

    for mc in mcs:
        plt.hist(sipms_mean, label=mc['name'], range=mc['r_mean'], bins=bins_mean)
    plt.xlabel('mean charge [pes] / microsecond / event')
    plt.title('SiPMs, '+mc['name'])
    plt.yscale('log')
    plt.legend()
    plt.savefig(outdir+'edges_mean_'+str(mc['size'])+'mm.png')
    plt.close()
