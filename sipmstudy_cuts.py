"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the energy resolution of the simulations
detector configuration.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from ic_functions import *

print("Starting")
nfiles = 10 # will fail if too few events
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
    mcs = [s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p6, s6p15] #s1p1, s1p7, s1p15, s3p3, s3p7, s3p15, s6p15] #, s3p7, s3p8, s3p9, s3p10, s3p15]                                                    

for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        mc["files"] = [indir+mc['teflon']+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]

cuts = [i*10 for i in range(0,200)]
for mc in mcs:
    sipm_response = pd.DataFrame()
    eff = {cut:pd.DataFrame() for cut in cuts}
    for file in mc['files']:
        print('Running over: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])

        # Sum up all charges per event in sipms
        sipm_response = sipm_response.append(sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999])
        this = sipm_response.groupby('event_id')
        total_charges = this.agg({"charge":"sum"})

        for cut in cuts:
            cut_sipm_response = sipm_response[sipm_response.charge > cut]
            this = cut_sipm_response.groupby('event_id')
            charges = this.agg({"charge":"sum"})
            eff[cut] = eff[cut].append(charges/total_charges)
            
    efficiencies = []
    for cut in cuts:
        efficiencies.append(eff[cut].charge.mean())# Calculate efficiencies based on threshold cut
    
    mc['eff'] = efficiencies
    #mc['sipms'] = sipm_response
    
if event_type == 'kr':
    event_str = '41.5 keV'
else:
    event_str = r'$Q_{\beta \beta}$'
"""
for mc in mcs:
    plt.hist(mc['sipms'].groupby('event_id').apply(lambda grp: grp.groupby('sensor_id').agg({'charge':'sum'})).charge, label=mc['name'])
plt.title('Signal per SiPM per event')
plt.xlabel('charge [pes]')
plt.legend()
plt.savefig(outdir+'cuts_charge.png')
plt.close()

for mc in mcs:
    plt.hist(mc['sipms'].groupby('event_id').apply(lambda grp: grp.groupby('sensor_id').agg({'charge':'sum'})).charge)
    plt.title('Signal per SiPM per event')
    plt.xlabel('charge [pes]')
    plt.savefig(outdir+'cuts_charge_'+mc['name']+'.png')
    plt.close()
"""
mcs_by_size = [[], [], []]
for mc in mcs:
    if mc['size'] == 1:
        mcs_by_size[0].append(mc)
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
    elif mc['size'] == 6:
        mcs_by_size[2].append(mc)
for mcs in mcs_by_size:
    for mc in mcs:
        plt.plot(cuts, mc['eff'], 'o', label=mc['name'])
    plt.xlabel('SiPM signal threshold [pes]')
    plt.ylabel('Signal after threshold / total signal')
    plt.title('SiPM Efficiency, '+event_str)
    plt.legend()
    plt.savefig(outdir+'cuts_eff_'+str(mc['size'])+'.png')
    plt.close()

    for mc in mcs:
        plt.plot(cuts, mc['eff'], 'o')
        plt.xlabel('SiPM signal threshold [pes]')
        plt.ylabel('Signal after threshold / total signal')
        plt.title('SiPM Efficiency, '+mc['name'])
        plt.savefig(outdir+'cuts_eff_'+mc['name']+'.png')
        plt.close()
