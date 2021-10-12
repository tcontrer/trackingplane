"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the time of events.
"""


import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from open_files import make_mc_dictionaries

print("Starting")
nfiles = 1
local = True
event_type = 'kr'
teflon = False

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

def split_in_peaks(indices, stride):
    where = np.where(np.diff(indices) > stride)[0]
    return np.split(indices, where + 1)

def FindFinalz(grp):
    final_z = grp[particles.mother_id==0][particles.particle_name=='e-'].final_z
    if not final_z.empty:
        return final_z.values[0]
    return

def GetWidth(event_response):
    event_id = event_response.event_id.values[0]
    time_bins = event_response.time_bin.drop_duplicates().sort_values()

    # Splits times into groups (peaks) to get blobs
    peaks = split_in_peaks(time_bins, 1)

    if len(peaks)==2:
        peak_timebins = peaks[1]
        thispeak_charges = event_response.loc[event_response.time_bin.isin(peak_timebins)].drop_duplicates()
        width = thispeak_charges.time_bin.values.max() - thispeak_charges.time_bin.values.min()
        return width
    return

for mc in mcs:
    sipm_timing = pd.DataFrame()
    sipm_timing_filtered = pd.DataFrame()

    for file in mc['files']:
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

        #sipm_response = sipm_response[sipm_response.event_id.isin(lowz_events)]
        widths = sipm_response.groupby('event_id').apply(
                        lambda grp: GetWidth(grp)).dropna()
        widths = pd.DataFrame({'event_id':widths.index, 'width':widths.values}).set_index('event_id')
        sipm_timing = sipm_timing.append(widths)

        # filter for low z events
        particles = pd.read_hdf(file, 'MC/particles')
        z_map = particles.groupby('event_id').apply(lambda grp: FindFinalz(grp)).dropna()
        z_map = pd.DataFrame({'event_id':z_map.index, 'z':z_map.values}).set_index('event_id')
        lowz_events = z_map[z_map.z<50.].index

        sipm_response = sipm_response[sipm_response.event_id.isin(lowz_events)]
        widths = sipm_response.groupby('event_id').apply(
                        lambda grp: GetWidth(grp)).dropna()
        widths = pd.DataFrame({'event_id':widths.index, 'width':widths.values}).set_index('event_id')
        sipm_timing_filtered = sipm_timing_filtered.append(widths)

    mc['sipm_times'] = np.array(sipm_timing.T.values).flatten()
    mc['sipm_times_f'] = np.array(sipm_timing_filtered.T.values).flatten()

if event_type == 'kr':
    time_range = (0,50)
else:
    time_range = (0, 250)

print("Plotting")

for mc in mcs:
    plt.hist(mc["sipm_times"], bins=20)#, range=time_range)
    plt.xlabel('Event width by SiPMs [microseconds]')
    plt.title('NEXT_100, '+mc['name'])
    plt.savefig(outdir+'time_'+mc['name']+"_sipm.png")
    plt.close()

    plt.hist(mc["sipm_times_f"], bins=20)#, range=time_range)
    plt.xlabel('Event width by SiPMs [microseconds]')
    plt.title('NEXT_100, '+mc['name']+', z < 50.')
    plt.savefig(outdir+'time_'+mc['dir']+"_lowz_sipm.png")
    plt.close()
