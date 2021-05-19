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
nfiles = 500 # will fail if too few events
local = False

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
    outdir = '/n/holystore01/LABS/guenette_lab/Users/tcontreras/trackingplane/plots/'
    indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"
    mcs = [s3p3, s3p7, s3p15] #, s3p7, s3p8, s3p9, s3p10, s3p15]
    
for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+'teflonhole_5mm/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    
    
for mc in mcs:
    
    all_sipms = pd.DataFrame()
    all_pmts = pd.DataFrame()
    events_allsensors = pd.DataFrame()
    events_allsipms = pd.DataFrame()
    events_allpmts = pd.DataFrame()
    for file in mc['files']:
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        
        # Sort to get the sipms
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Sort to sum up all charges for each sipms
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        response_byid = sipm_response.groupby('sensor_id')
        summed_charges = response_byid.agg({"charge":"sum"}) 

        # Make data frame with sipms ids, position, and total charge
        new_sipm_positions = sipm_positions.set_index('sensor_id')
        new_df = pd.concat([new_sipm_positions.iloc[:,1:5], summed_charges], axis=1)
        all_sipms = all_sipms.append(new_df)

        # pmts
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        response_byid_pmt = pmt_response.groupby('sensor_id')
        summed_charges_pmt = response_byid_pmt.agg({"charge":"sum"})
        pmt_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("Pmt")]
        new_pmt_positions = pmt_positions.set_index('sensor_id')
        new_df_pmt = pd.concat([new_pmt_positions.iloc[:,1:5], summed_charges_pmt], axis=1)
        all_pmts = all_pmts.append(new_df_pmt)

    mc['all_sipms'] = all_sipms
    mc['all_pmts'] = all_pmts
    
for mc in mcs:
    plt.hist(mc['all_sipms'].charge, label='sipms', range=(0,85000), bins=100)
    plt.hist(mc['all_pmts'].charge, label='pmts', range=(0,85000), bins=100)
    plt.xlabel("Charge per event [pes]")
    plt.title("NEXT-100, 3mm sipms, "+str(mc['pitch'])+' pitch')
    plt.legend()
    plt.savefig(outdir+'energy_distr_'+mc['dir']+'.png')
    plt.close()
    
for mc in mcs:
    plt.hist(mc['all_sipms'].charge, label=mc['dir'], range=(0,5000), bins=100)
plt.xlabel("Charge per event in SiPMs [pes]")
plt.title("NEXT-100, 3mm sipms")
plt.legend()
plt.savefig(outdir+'sipm_energy_distr_comp.png')
plt.close()

for mc in mcs:
    plt.hist(mc['all_pmts'].charge, label=mc['dir'], range=(0,100000), bins=100)
plt.xlabel("Charge per event in PMTs [pes]")
plt.title("NEXT-100, 3mm sipms")
plt.legend()
plt.savefig(outdir+'pmt_energy_distr_comp.png')
plt.close()

