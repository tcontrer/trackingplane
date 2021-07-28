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
s3p10 = {"size":3, "pitch":10, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 10mm pitch',"dir": "s3mmp10mm"}
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
    mcs = [s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p6, s6p15] #, s3p7, s3p8, s3p9, s3p10, s3p15]                                                    

for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+mc['teflon']+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]

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
