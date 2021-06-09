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

def Thresh_by_Event(group, args=dark_count):
    event = group.index.tolist()[0] #.event_id.max()
    thresh = dark_count.loc[event].dark_count
    return group[group.charge > thresh]

print("Starting")
nfiles = 99 # fails if there are not enough events
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

    sipm_map = pd.DataFrame()
    pmt_pmt = pd.DataFrame()
    for file in mc['files']:
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')

        # Sort to get the sipm positions
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Create separate dataframes for the sipm and pmt response
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]

        # Time length of events
        pmt_timing = pmt_timing.append(pmt_response.groupby(['event_id'])\
                        .apply(lambda group: group['time_bin'].max() - group['time_bin'].min()).to_frame())
        sipm_timing = sipm_timing.append(sipm_response.groupby(['event_id'])\
                        .apply(lambda group: group['time_bin'].max() - group['time_bin'].min()).to_frame())


        # Summed pmt energy per event
        response_perevent_pmt = pmt_response.groupby('event_id')
        summed_charges_byevent_pmt = response_perevent_pmt.agg({"charge":"sum"})

        # Summed sipm energy per event
        response_perevent_sipm = sipm_response.groupby('event_id')
        summed_charges_byevent_sipm = response_perevent_sipm.agg({"charge":"sum"})

        sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]

        dark_rate = 10.
        dark_count  = sipm_timing*dark_rate
        dark_count = dark_count.rename(columns={0:'dark_count'})
        this = summed_charges_byevent_sipm.groupby('event_id')
        summed_charged_byevent_sipm = this.apply(Thresh_by_Event, args=(dark_count))#.set_index('event_id') #.groupby('event_id')


        # Position of the event(sipm with the max charge)
        sipm_response = sipm_response[sipm_response.event_id.isin(summed_charges_byevent_sipm.index)]
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
    plt.savefig(outdir+'map_sipm_'+mc['name']+event_type+'.png')
    plt.close()

    h2 = hist2d(mc['pmt_map'].x, mc['pmt_map'].y, (nbins, nbins), weights = mc['pmt_map'].charge)
    labels("X [mm]", "Y [mm]", "PMTs Light Distribution \n (NEXT-100)")
    plt.savefig(outdir+'map_pmt_'+mc['name']+event_type+'.png')
    plt.close()
