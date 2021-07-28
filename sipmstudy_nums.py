"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and produces a krypton map showing the energy distribution in xy.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

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

pitches = ['fullcoverage', 7, 15]
sizes = [1, 1.3, 3, 6]
teflon = 'teflonhole_5mm'

if local:
    outdir = '/Users/taylorcontreras/Development/Research/trackingplane/'
    indir = outdir
    pitches = [15]
    sizes = [3]
else:
    if event_type == 'kr':
        outdir = '/n/home12/tcontreras/plots/trackingplane/krypton/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/"
    else:
        outdir = '/n/home12/tcontreras/plots/trackingplane/highenergy/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"

# Create dictionary to hold run info
print("Creating dictionaries")
mcs = []
for size in sizes:
    for pitch in pitches:
        this_pitch = pitch
        mc = {'size': size, 'pitch':this_pitch}
        dir = 's'+str(size)+'mmp'+str(this_pitch)+'mm'
        if pitch == 'fullcoverage':
            this_pitch = size
            mc['extra_dir'] = dir
            dir = pitch
        mc['dir'] = dir
        mc['name'] = str(size)+'mm SiPM, '+str(this_pitch)

        if mc['dir'] == "fullcoverage":
            mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
        else:
            if not local:
                mc["files"] = [indir+teflon+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
            else:
                mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]


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
