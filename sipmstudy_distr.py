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
nfiles = 20 # will fail if too few events
local = False
event_str = 'kr'

# Create dictionary to hold run info
print("Creating dictionaries")
s3p3 = {"size":3, "pitch":3, "dir":"fullcoverage"}
s3p6 = {"size":3, "pitch":6, "dir": "s3mmp6mm"}
s3p7 = {"size":3, "pitch":7, "dir": "s3mmp7mm"}
s3p8 = {"size":3, "pitch":8, "dir": "s3mmp8mm"}
s3p9 = {"size":3, "pitch":9, "dir": "s3mmp9mm"}
s3p10 = {"size":3, "pitch":10, "dir": "s3mmp9mm"}
s3p15 = {"size":3, "pitch":15, "dir": "s3mmp15mm"}

if local:
    outdir = '/Users/taylorcontreras/Development/Research/trackingplane/'
    indir = outdir
    mcs = [s3p15]
else:
    if event_str == 'kr'
        outdir = '/n/holystore01/LABS/guenette_lab/Users/tcontreras/trackingplane/plots/krypton/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/" 
        extra_dir = 's3mmp3mm'
    else:
        outdir = '/n/holystore01/LABS/guenette_lab/Users/tcontreras/trackingplane/plots/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"
        extra_dir = ''
    mcs = [s3p3, s3p7, s3p15] #, s3p7, s3p8, s3p9, s3p10, s3p15]
    
for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+extra_dir+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+'teflonhole_5mm/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    
    
for mc in mcs:
    
    sipms = pd.DataFrame()
    pmts = pd.DataFrame()
    for file in mc['files']:
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])

        # Sum up all charges per event in sipms
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        sipm_response_byevent = sipm_response.groupby('event_id')
        charges = sipm_response_byevent.agg({"charge":"sum"})
        sipms = sipms.append(charges)
        
        # Sum up all charges per event in pmts
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        pmt_response_byevent = sipm_response.groupby('event_id')
        charges = sipm_response_byevent.agg({"charge":"sum"})
        pmts = pmts.append(charges)
    

    mc['sipms'] = sipms
    mc['pmts'] = pmts
    
if event_type == 'kr':
    sipm_range = (0, 85000)
    pmt_range = (0, 85000)
else:
    sipm_range = (0, 5000)
    pmt_range = (0, 100000)
    
    
for mc in mcs:
    plt.hist(mc['sipms'].charge, label='sipms', range=sipm_range, bins=100)
    plt.xlabel("Charge per event [pes]")
    plt.title("NEXT-100, 3mm sipms, "+str(mc['pitch'])+' pitch')
    plt.legend()
    plt.savefig(outdir+'energy_distr_'+mc['dir']+'.png')
    plt.close()

for mc in mcs:
    plt.hist(mc['sipms'].charge, label='sipms', range=pmt_range, bins=100)
    plt.xlabel("Charge per event [pes]")
    plt.title("NEXT-100, 3mm sipms, "+str(mc['pitch'])+' pitch')
    plt.legend()
    plt.savefig(outdir+'energy_distr_'+mc['dir']+'.png')
    plt.close()
    
for mc in mcs:
    plt.hist(mc['all_sipms'].charge, label=mc['dir'], range=sipm_range, bins=100)
plt.xlabel("Charge per event in SiPMs [pes]")
plt.title("NEXT-100, 3mm sipms")
plt.legend()
plt.savefig(outdir+'sipm_energy_distr_comp.png')
plt.close()

for mc in mcs:
    plt.hist(mc['all_pmts'].charge, label=mc['dir'], range=pmt_range, bins=100)
plt.xlabel("Charge per event in PMTs [pes]")
plt.title("NEXT-100, 3mm sipms")
plt.legend()
plt.savefig(outdir+'pmt_energy_distr_comp.png')
plt.close()

