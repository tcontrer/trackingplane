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

from ic_functions import *

print("Starting")
nfiles = 2 # will fail if too few events
local = False
event_type = 'kr'

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
    mcs = [s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p6] #, s3p7, s3p8, s3p9, s3p10, s3p15]
    
for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+mc['teflon']+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    
    
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
    

    mc['sipms'] = sipms
    mc['pmts'] = pmts
    
if event_type == 'kr':
    sipm_range = (0, 350000)
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

