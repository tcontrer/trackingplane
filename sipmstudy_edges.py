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


print("Starting")
nfiles = 100 # will fail if too few events
local = False
event_type = 'kr'
teflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:
    sipms = pd.DataFrame()

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
        sipms = sipms.append(sipm_response)

    b =100
    r =(0,100)
    if mc['size'] == 1:
        b = 60
        r = (0,60)
    elif mc['size'] == 3:
        b = 100
        r = (0,600)
    elif mc['size'] == 6:
        b = 100
        r = (0,2500)
    plt.hist(sipms.charge, bins=b, range=r)
    plt.xlabel('charge [pes] / microsecond')
    plt.title('SiPMs, '+mc['name'])
    plt.yscale('log')
    plt.savefig(outdir+'edges_'+mc['name']+'.png')
    plt.close()
