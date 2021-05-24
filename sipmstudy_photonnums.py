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


print("Starting")
nfiles = 10 # will fail if too few events
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
    
# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    top_sipms = pd.DataFrame()

    for file in mc["files"]:
        print("Looping files in mc")
        sns_response = pd.read_hdf(file, 'MC/sns_response')

        # Sort to sum up all charges for each sipms
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

        top_10_sipms = sipm_response.groupby('event_id',as_index=False).apply(lambda grp: grp.nlargest(10,'charge'))
        top_sipms_by_event = top_10_sipms.groupby('event_id')

    mc["top_sipms"] = [top_sipms_by_event.apply(lambda grp: grp.iloc[i]) for i in range(0,10)]

print("Plotting")
# Plot each i-th sipm for each mc
for mc in mcs:
    print('')
    print(mc['top_sipms'][0]['charge'])
    print(mc['top_sipms'])
    for i in range(0,10):
        plt.hist(mc['top_sipms'][i]['charge'])
        plt.xlabel('charge [pes]')
        plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch, '+str(i)+' largest sipm signal per event')
        plt.savefig(outdir+mc['dir']+"_"+str(i)+"largest_sipm.png")
        plt.close()

# Plot top 5 sipms for each mc
for mc in mcs:
    for i in range(0,5):
        plt.hist(mc['top_sipms'][i]['charge'], alpha=0.5, label=str(i))
    plt.xlabel('charge [pes]')
    plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.legend()
    plt.savefig(outdir+mc['dir']+"largests_5sipms_comp.png")
    plt.close()

# Plot top i-th sipm across mcs
for i in range(0,10):
    for mc in mcs:
        plt.hist(mc['top_sipms'][i]['charge'], alpha=0.5, label=str(mc['size'])+" sipms, "+str(mc['pitch'])+" pitch")
    plt.xlabel('charge [pes]')
    plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(i)+" largest sipm signal per event")
    plt.legend()
    plt.savefig(outdir+str(i)+"largest_sipm_comp.png")
    plt.close()
