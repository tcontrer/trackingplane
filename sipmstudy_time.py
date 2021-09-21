"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the time of events.
"""


import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from open_files import make_mc_dictionaries

print("Starting")
nfiles = 500
local = False
event_type = 'qbb'
teflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:
    sipm_timing = pd.DataFrame()
    pmt_timing = pd.DataFrame()
    for file in mc['files']:
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]

        pmt_timing = pmt_timing.append(pmt_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)
        sipm_timing = sipm_timing.append(sipm_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)

    mc["pmt_times"] = np.array(pmt_timing.T.values).flatten()
    mc['sipm_times'] = np.array(sipm_timing.T.values).flatten()

if event_type == 'kr':
    time_range = (0,50)
else:
    time_range = (0, 250)

print("Plotting")
for mc in mcs:
    plt.hist(mc["pmt_times"], bins=20)
    plt.xlabel('Event width by PMTs [microseconds]')
    plt.title('NEXT_100, '+mc['name'])
    plt.savefig(outdir+'time_'+mc['name']+"_pmt.png")
    plt.close()

for mc in mcs:
    plt.hist(mc["sipm_times"], bins=20, range=time_range)
    plt.xlabel('Event width by SiPMs [microseconds]')
    plt.title('NEXT_100, '+mc['name'])
    plt.savefig(outdir+'time_'+mc['name']+"_sipm.png")
    plt.close()
