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
nfiles = 5 # will fail if too few events
local = False
event_type = 'kr'

pitches = ['fullcoverage', 7, 15]
sizes = [1.3, 3, 6]
teflon = 'no_teflon' #'teflonhole_5mm'

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
                mc['extra_dir'] = 's'+str(size)+'mmp'+str(this_pitch)+'mm/'
                dir = 'fullcoverage'
            else:
                dir = 's'+str(size)+'mmp'+str(this_pitch)+'mm/'
                mc = {'size': size, 'pitch':this_pitch}

            mc['dir'] = dir
            mc['name'] = str(size)+'mm SiPM, '+str(this_pitch)

            if mc['dir'] == "fullcoverage":
                mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
            else:
                if not local:
                    mc["files"] = [indir+teflon+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
                else:
                    mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
            mcs.append(mc)

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


    mc['sipms'] = sipms[sipms.charge>0]
    mc['pmts'] = pmts[pmts.charge>0]
    if mc['size'] == 6:
        print(sipms[sipms.charge < 10000].mean)

if event_type == 'kr':
    sipm_range = (0, 400000)
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
