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

# Create dictionary to hold run info
print("Creating dictionaries")
s1p1 = {"size":1, "pitch":1, 'teflon':'no_teflon', 'name':'1mm SiPM, full coverage', "dir":"fullcoverage", 'extra_dir':'/s1mmp1mm'}
s1p7 = {"size":1, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 7mm pitch',"dir": "s1mmp7mm"}
s1p15 = {"size":1, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 15mm pitch',"dir": "s1mmp15mm"}
s3p3 = {"size":3, "pitch":3, 'teflon':'no_teflon', 'name':'3mm SiPM, full coverage', "dir":"fullcoverage", 'extra_dir':'/s3mmp3mm'}
s3p6 = {"size":3, "pitch":6, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 6mm pitch',"dir": "s3mmp6mm"}
s3p7 = {"size":3, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 7mm pitch',"dir": "s3mmp7mm"}
s3p8 = {"size":3, "pitch":8, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 8mm pitch',"dir": "s3mmp8mm"}
s3p9 = {"size":3, "pitch":9, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 9mm pitch',"dir": "s3mmp9mm"}
s3p10 = {"size":3, "pitch":10, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 10mm pitch',"dir": "s3mmp9mm"}
s3p15 = {"size":3, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 15mm pitch', "dir": "s3mmp15mm"}
s6p6 = {"size":6, "pitch":6,'teflon':'no_teflon', 'name':'6mm SiPM, full coverage', "dir":"fullcoverage", 'extra_dir':'/s6mmp6mm'}
s6p7 = {"size":6, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '6mm SiPM, 7mm pitch',"dir": "s6mmp7mm"}
s6p15 = {"size":6, "pitch":15, 'teflon':'teflonhole_8mm', 'name': '6mm SiPM, 15mm pitch', "dir": "s6mmp15mm"}

if local:
    outdir = '/Users/taylorcontreras/Development/Research/trackingplane/'
    indir = outdir
    mcs = [s3p15]
else:
    if event_type == 'kr':
        outdir = '/n/home12/tcontreras/plots/trackingplane/krypton/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/"
    else:
        outdir = '/n/home12/tcontreras/plots/trackingplane/highenergy/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"
    mcs = [s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p6, s6p15] #s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p6] #, s3p7, s3p8, s3p9, s3p10, s3p15]                                                    

for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+mc['teflon']+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]


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
