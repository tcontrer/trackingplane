"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and produces a krypton map showing the energy distribution in xy.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from open_files import make_mc_dictionaries

from ic_functions import *

def Thresh_by_Event(group, dark_count):
    event = group.index.tolist()[0] #.event_id.max()
    thresh = dark_count.loc[event].dark_count
    return group[group.charge > thresh]

print("Starting")
nfiles = 1 # fails if there are not enough events
local = False
event_type = 'kr'
dark_rate = {1:80, 3: 450, 6: 1800} # SiPM size: average dark rate per sipm
teflon = True

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:

    sipm_map = pd.DataFrame()
    pmt_map = pd.DataFrame()
    pmt_timing = pd.DataFrame()
    sipm_timing = pd.DataFrame()
    for file in mc['files']:
        print('Running over: '+file+'---------------------------------')
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file")
            continue
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')

        # Sort to get the sipm positions
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        print(mc['name'])
        print('Number of sipms = '+str(len(sipm_positions.sensor_id.values)))
