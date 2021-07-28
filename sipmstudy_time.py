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

print("Starting")
nfiles = 500
local = False
event_type = 'qbb'

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
        if size == 6 and pitch == 7:
            pass
        else:
            this_pitch = pitch
            if pitch == 'fullcoverage':
                this_pitch = size
                mc = {'size': size, 'pitch':this_pitch}
                mc['extra_dir'] = 's'+str(size)+'mmp'+str(this_pitch)+'mm'
                dir = 'fullcoverage'
            else:
                dir = 's'+str(size)+'mmp'+str(this_pitch)+'mm'
                mc = {'size': size, 'pitch':this_pitch}
            mc['dir'] = dir
            mc['name'] = str(size)+'mm SiPM, '+str(this_pitch)

            if mc['dir'] == "fullcoverage":
                mc["files"] = [indir+mc['dir']+'/'+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
            else:
                if not local:
                    mc["files"] = [indir+teflon+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
                else:
                    mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
            mcs.append(mc)


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
