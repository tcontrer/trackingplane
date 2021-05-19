"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the time of events.
"""


import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

print("Starting")
nfiles = 1
local = False

# Create dictionary to hold run info
print("Creating dictionaries")
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
    indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/teflonhole_5mm/"
    mcs = [s3p6] #, s3p7, s3p8, s3p9, s3p10, s3p15]
    
for mc in mcs:
    mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]


# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
pmt_time_binning = .025 # microseconds (25ns)
sipm_time_binning = 1.0 # microseconds
for mc in mcs:
    print("Looping in mcs")
    sipm_timing = pd.DataFrame()
    pmt_timing = pd.DataFrame()

    for file in mc["files"]:
        print("Looping files in mc")
        # Get all sensor responses and all the sensor positions
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]

        pmt_timing = pmt_timing.append(pmt_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)
        sipm_timing = sipm_timing.append(sipm_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)

    mc["pmt_times"] = pmt_timing
    mc['sipm_times'] = sipm_timing

print("Plotting")
for mc in mcs:
    plt.hist(mc["pmt_times"], bins=50, range=(0,2000))
    plt.xlabel('Event width by PMTs [microseconds]')
    plt.title('NEXT_100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.savefig(outdir+mc['dir']+"_pmt_times.png")
    plt.close()

for mc in mcs:
    plt.hist(mc["sipm_times"], bins=50, range=(0,2000))
    plt.xlabel('Event width by SiPMs [microseconds]')
    plt.title('NEXT_100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.savefig(outdir+mc['dir']+"_sipm_times.png")
    plt.close()
