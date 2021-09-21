"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and produces a krypton map showing the energy distribution in xy.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from open_files import make_mc_dictionaries

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
nfiles = 10 # fails if there are not enough events
local = False
event_type = 'kr'
teflon = False

dark_rate = {1:80./1000., 3: 450./1000., 6: 1800./1000.} # SiPM size: average dark rate per sipm (counts/microsecond)
if event_type == 'kr':
    event_time = 15. # microseconds
else:
    event_time = 200. # microseconds

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    pmt_map = pd.DataFrame()
    sipm_map = pd.DataFrame()
    pmt_timing = pd.DataFrame()
    sipm_timing = pd.DataFrame()

    sipm_map = pd.DataFrame()
    pmt_map = pd.DataFrame()
    pmt_timing = pd.DataFrame()
    sipm_timing = pd.DataFrame()
    for file in mc['files']:
        print('Running over: '+file+'---------------------------------')
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file")
            continue
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')

        # Sort to get the sipm positions
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Create separate dataframes for the sipm and pmt response
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        #if not sipm_response.loc[sipm_response["time_bin"] >0].empty:
        #    sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        #    pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]

        # Time length of events
        #pmt_timing = pmt_response.groupby(['event_id'])\
        #                        .apply(lambda group: group['time_bin'].max() - group['time_bin'].min())
        #sipm_timing = sipm_response.groupby(['event_id'])\
        #                        .apply(lambda group: group['time_bin'].max() - group['time_bin'].min())

        # Summed pmt energy per event
        response_perevent_pmt = pmt_response.groupby('event_id')
        summed_charges_byevent_pmt = response_perevent_pmt.agg({"charge":"sum"})

        # Summed sipm energy per event
        response_perevent_sipm = sipm_response.groupby('event_id')
        summed_charges_byevent_sipm = response_perevent_sipm.agg({"charge":"sum"})

        # Estimated dark count
        #print('Before: ', summed_charges_byevent_sipm)
        #dark_count = dark_rate[mc['size']]*event_time
        #summed_charges_byevent_sipm = summed_charges_byevent_sipm[summed_charges_byevent_sipm.charge > dark_count]
        #print('Dark count: ', dark_count)
        #print('After: ', summed_charges_byevent_sipm)

        #print('sipm_response: ', sipm_response)
        #print('timing: ', sipm_timing)
        # Threshold event above estimated dark count in event
        #dark_count  = sipm_timing*dark_rate[mc['size']]
        #print('dark_count: ', dark_count)
        #print(dark_count.to_frame().rename(columns={0:'dark_count'}))
        #dark_count = dark_count.to_frame().rename(columns={0:'dark_count'})
        #this = summed_charges_byevent_sipm.groupby('event_id')
        #summed_charged_byevent_sipm = this.apply(Thresh_by_Event, (dark_count))#.set_index('event_id') #.groupby('event_id')


        # Position of the event(sipm with the max charge)
        sipm_response = sipm_response[sipm_response.event_id.isin(summed_charges_byevent_sipm.index)]
        idx = sipm_response.groupby(['event_id'])['charge'].transform(max) == sipm_response['charge']
        max_sipms = sipm_response[idx].sort_values('sensor_id').set_index('sensor_id')
        new_max_sipm_positions = sipm_positions.set_index('sensor_id')
        this = new_max_sipm_positions.loc[max_sipms.index.values.tolist()]
        event_map = pd.concat([max_sipms.loc[:,'event_id'],this.loc[:,['x','y','z']]], axis=1).set_index('event_id').sort_values(by='event_id')

        print('event map:', event_map[event_map.duplicated()])
        print('sumed charges: ', summed_charges_byevent_sipm[summed_charges_byevent_sipm.duplicated()])

    #mc["pmt_map"] = pmt_map
    mc["sipm_map"] = sipm_map

nbins = 500//10
for mc in mcs:
    h = hist2d(mc['sipm_map'].x, mc['sipm_map'].y, (nbins, nbins), weights = mc['sipm_map'].charge)
    labels("X [mm]", "Y [mm]", "SiPMs Light Distribution \n (NEXT-100, "+mc['name']+")")
    plt.savefig(outdir+'map_sipm_'+mc['name']+event_type+'.png')
    plt.close()

    #h2 = hist2d(mc['pmt_map'].x, mc['pmt_map'].y, (nbins, nbins), weights = mc['pmt_map'].charge)
    #labels("X [mm]", "Y [mm]", "PMTs Light Distribution \n (NEXT-100)")
    #plt.savefig(outdir+'map_pmt_'+event_type+'.png')
    #plt.close()
