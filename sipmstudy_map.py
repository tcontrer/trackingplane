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


print("Starting")
nfiles = 10 # fails if there are not enough events
local = False
event_type = 'kr'

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
    if event_type == 'kr':
        outdir = '/n/holystore01/LABS/guenette_lab/Users/tcontreras/trackingplane/plots/krypton/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/" 
        extra_dir = '/s3mmp3mm'
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
    
# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    pmt_map = pd.DataFrame()
    sipm_map = pd.DataFrame()

    for file in mc["files"]:
        print("Looping files in mc")
        # Get all sensor responses and all the sensor positions
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')

        # Sort to get the sipm positions
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Create separate dataframes for the sipm and pmt response
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]

        # Summed pmt energy per event
        response_perevent_pmt = pmt_response.groupby('event_id')
        summed_charges_byevent_pmt = response_perevent_pmt.agg({"charge":"sum"})

        # Summed sipm energy per event
        response_perevent_sipm = sipm_response.groupby('event_id')
        summed_charges_byevent_sipm = response_perevent_sipm.agg({"charge":"sum"})

        # Position of the event(sipm with the max charge)
        idx = sipm_response.groupby(['event_id'])['charge'].transform(max) == sipm_response['charge']
        max_sipms = sipm_response[idx].sort_values('sensor_id').set_index('sensor_id')
        new_max_sipm_positions = sipm_positions.set_index('sensor_id')
        this = new_max_sipm_positions.loc[max_sipms.index.values.tolist()]
        event_map = pd.concat([max_sipms.loc[:,'event_id'],this.loc[:,['x','y','z']]], axis=1).set_index('event_id').sort_values(by='event_id') 
        
        pmt_map = pmt_map.append(pd.concat([summed_charges_byevent_pmt,event_map],axis=1))
        sipm_map = sipm_map.append(pd.concat([summed_charges_byevent_sipm,event_map],axis=1))

    mc["pmt_map"] = pmt_map
    mc["sipm_map"] = sipm_map

nbins = 500//10
for mc in mcs:
    h = hist2d(mc['sipm_map'].x, mc['sipm_map'].y, (nbins, nbins), weights = mc['sipm_map'].charge)
    labels("X [mm]", "Y [mm]", "SiPMs Light Distribution \n (NEXT-100, 6mm sipms, 10mm pitch)")
    plt.savefig(outdir+'sipm_kr_map.png')
    plt.close()

    h2 = hist2d(mc['pmt_map'].x, mc['pmt_map'].y, (nbins, nbins), weights = mc['pmt_map'].charge)
    labels("X [mm]", "Y [mm]", "PMTs Light Distribution \n (NEXT-100)")
    plt.savefig(outdir+'pmt_kr_map.png')
    plt.close()
