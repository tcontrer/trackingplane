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

#dark_count = []
def Thresh_by_Event(group, dark_count):
    event = group.index.tolist()[0] #.event_id.max()
    thresh = dark_count.loc[event].dark_count
    return group[group.charge > thresh]

def Center_of_Event(sipm_response_in_event, sipm_positions):
    top_sipms = sipm_response_in_event[sipm_response_in_event.charge > max(sipm_response_in_event.charge)*.1]
    sensor_positions = sipm_positions.loc[sipm_positions.sensor_id.isin(top_sipms.sensor_id.tolist())]
    sensor_positions = sensor_positions.reindex(sensor_positions.index.repeat(top_sipms.groupby('sensor_id').sensor_id.count().values))
    top_sipms = top_sipms.merge(sensor_positions)
    
    x = np.sum(top_sipms.charge*top_sipms.x)/np.sum(top_sipms.charge)
    y = np.sum(top_sipms.charge*top_sipms.y)/np.sum(top_sipms.charge)
    z = np.sum(top_sipms.charge*top_sipms.z)/np.sum(top_sipms.charge)
    charge = np.sum(top_sipms.charge)
    event_id = top_sipms.event_id[0]
    
    return pd.Series({'event_id':event_id, 'charge':charge,'x':x, 'y':y, 'z':z})

print("Starting")
nfiles = 1 # fails if there are not enough events
local = True
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
        outdir = '/n/home12/tcontreras/plots/trackingplane/krypton/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/" 
        extra_dir = '/s3mmp3mm'
    else:
        outdir = '/n/home12/tcontreras/plots/trackingplane/highenergy/'
        indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"
        extra_dir = ''
    mcs = [s3p3, s3p7, s3p15] #, s3p7, s3p8, s3p9, s3p10, s3p15]
    
for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+extra_dir+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        if not local:
            mc["files"] = [indir+'teflonhole_5mm/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
        else:
            mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    
# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    pmt_map = pd.DataFrame()
    sipm_map = pd.DataFrame()
    pmt_timing = pd.DataFrame()
    sipm_timing = pd.DataFrame()

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
        
        dark_rate = 10.
        dark_count  = sipm_timing*dark_rate
        dark_count = dark_count.rename(columns={0:'dark_count'})
        this = summed_charges_byevent_sipm.groupby('event_id')
        summed_charged_byevent_sipm = this.apply(Thresh_by_Event, (dark_count))#.set_index('event_id') #.groupby('event_id')

        # Position of the event(sipm with the max charge)
        sipm_map = sipm_map.append(sipm_response.groupby('event_id').apply(Center_of_Event, sipm_positions))
        
    #mc["pmt_map"] = pmt_map
    mc["sipm_map"] = sipm_map

nbins = 500//10
for mc in mcs:
    h = hist2d(mc['sipm_map'].x, mc['sipm_map'].y, (nbins, nbins), weights = mc['sipm_map'].charge)
    labels("X [mm]", "Y [mm]", "SiPMs Light Distribution \n (NEXT-100, 6mm sipms, 10mm pitch)")
    plt.savefig(outdir+'map_sipm_'+event_type+'.png')
    plt.close()

    #h2 = hist2d(mc['pmt_map'].x, mc['pmt_map'].y, (nbins, nbins), weights = mc['pmt_map'].charge)
    #labels("X [mm]", "Y [mm]", "PMTs Light Distribution \n (NEXT-100)")
    #plt.savefig(outdir+'map_pmt_'+event_type+'.png')
    #plt.close()
