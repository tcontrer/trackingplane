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
from scipy.optimize import curve_fit
from scipy.stats import norm
from fit_functions import fit_energy, plot_fit_energy, print_fit_energy, get_fit_params
from open_files import make_mc_dictionaries

from ic_functions import *
from invisible_cities.core.core_functions  import shift_to_bin_centers

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

    r = np.sqrt(x**2 + y**2 + z**2)

    return pd.Series({'event_id':event_id, 'charge':charge,'x':x, 'y':y, 'z':z, 'r':r})

print("Starting")
nfiles = 100 # will fail if too few events
local = False
event_type = 'kr'
teflon = False

tp_area = np.pi * (984./2.)**2 # mm^2
dark_rate = {1:80./1000., 3: 450./1000., 6: 1800./1000.} # SiPM size: average dark rate per sipm (counts/microsecond)
if event_type == 'kr':
    event_time = 20. # microseconds
else:
    event_time = 100. # microseconds

mcs_to_use = ['s13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

for mc in mcs:
    sipms = pd.DataFrame()
    pmts = pd.DataFrame()
    sipm_timing = pd.DataFrame()
    pmt_timing = pd.DataFrame()

    for file in mc['files']:

        print('Running over: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Sum up all charges per event in sipms
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        #print('sipm_response before: ', sipm_response)
        #if not sipm_response.loc[sipm_response["time_bin"] >0].empty:
        #    sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        #    pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]
        #print('sipm_response after: ', sipm_response)


        # Filter by R
        event_centers = sipm_response.groupby('event_id').apply(lambda grp: Center_of_Event(grp, sipm_positions))
        sipm_response = sipm_response[sipm_response.event_id.isin(event_centers[event_centers.r < 450].event_id)]
        pmt_response = pmt_response[pmt_response.event_id.isin(event_centers[event_centers.r < 450].event_id)]

        # Sum up all charges per event in sipms
        sipm_response_byevent = sipm_response.groupby('event_id')
        #sum_sipms_byevent = sipm_response_byevent.apply(lambda group: group.groupby('sensor_id').agg({"charge":"sum"})).groupby('event_id')
        #above_thresh_sipms = sum_sipms_byevent.apply(lambda group: group[group.charge > dark_rate[mc['size']]*event_time])
        charges = sipm_response_byevent.agg({"charge":"sum"})
        sipms = sipms.append(charges, ignore_index=True)

        # Sum up all charges per event in pmts
        pmt_response_byevent = pmt_response.groupby('event_id')
        charges = pmt_response_byevent.agg({"charge":"sum"})
        pmts = pmts.append(charges)

        # Time length of events
        #pmt_timing = pmt_timing.append(pmt_response.groupby(['event_id'])\
        #            .apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)
        #sipm_timing = sipm_timing.append(sipm_response.groupby(['event_id'])\
        #                                 .apply(lambda group: group['time_bin'].max() - group['time_bin'].min()), ignore_index=True)
        #print('timing: ', sipm_timing)

    # Threshold event based on dark noise
    #this = sipms.groupby('event_id')
    #dark_rate = 10.
    #dark_count  = sipm_timing*dark_rate
    #dark_count = dark_count.rename(columns={0:'dark_count'})
    #sipms = this.apply(Thresh_by_Event, (dark_count))#.set_index('event_id') #.groupby('event_id')

    sns_positions = pd.read_hdf(file, 'MC/sns_positions')
    sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
    sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]
    mc['num_sipms'] = len(sipm_positions)
    mc['coverage'] = 100. * len(sipm_positions) * mc['size']**2 / tp_area
    mc['sipms'] = sipms
    mc['pmts'] = pmts
    #mc['dark_count'] = dark_count.mean()

mc_sizes = [[], [], []]
for mc in mcs:
    if mc['size'] == 1 or mc['size'] == 1.3:
        mc_sizes[0].append(mc)
    elif mc['size'] == 3:
        mc_sizes[1].append(mc)
    elif mc['size'] == 6:
        mc_sizes[2].append(mc)

for mc in mcs:
    bins_fit = 50
    if event_type == 'kr':
        fit_range_sipms = (np.min(mc['sipms'].charge), np.max(mc['sipms'].charge)) #np.mean(np.mean(mc['sipms'].charge)-np.std(mc['sipms'].charge), np.mean(mc['sipms'].charge)+np.std(mc['sipms'].charge))
        fit_range_pmts = (np.min(mc['pmts'].charge), np.max(mc['pmts'].charge)) #np.mean(mc['pmts'].charge)-np.std(mc['pmts'].charge), np.mean(mc['pmts'].charge)+np.std(mc['pmts'].charge))
    else:
        y, b = np.histogram(mc['sipms'].charge, bins= bins_fit, range=[np.min(mc['sipms'].charge), np.max(mc['sipms'].charge)])
        x = shift_to_bin_centers(b)
        peak = x[np.argmax(y)]
        fit_range_sipms = (peak - np.std(mc['sipms'].charge)/10., peak + np.std(mc['sipms'].charge)/10.)

        y, b = np.histogram(mc['pmts'].charge, bins= bins_fit, range=[np.min(mc['pmts'].charge), np.max(mc['pmts'].charge)])
        x = shift_to_bin_centers(b)
        peak = x[np.argmax(y)]
        fit_range_pmts = (peak - np.std(mc['pmts'].charge), peak + np.std(mc['pmts'].charge))

        #fit_range_sipms = (np.mean(mc['sipms'].charge) - np.std(mc['sipms'].charge), np.mean(mc['sipms'].charge) + np.std(mc['sipms'].charge))
        #fit_range_pmts = (np.mean(mc['pmts'].charge) - np.std(mc['sipms'].charge), np.mean(mc['pmts'].charge) + np.std(mc['pmts'].charge))

    #print(mc['dir']+': Average Dark count = '+str(mc['dark_count']))

    sipm_fit = fit_energy(mc['sipms'].charge, bins_fit, fit_range_sipms)
    mc['sipm_eres'], mc['sipm_fwhm'], mc['sipm_mean'], mc['sipm_eres_err'], mc['sipm_fwhm_err'], mc['sipm_mean_err'] = get_fit_params(sipm_fit)
    print(mc['name']+'-------------------')
    print('SiPMs --------')
    print('Covergae: '+str(mc['coverage']))
    print('Response: ', mc['sipms'])
    print('Mean and std', np.mean(mc['sipms'].charge), np.std(mc['sipms'].charge))
    print_fit_energy(sipm_fit)
    plot_fit_energy(sipm_fit)
    plt.xlabel('charge [pes]')
    plt.title('Energy Resolution Fit, '+mc['name'])
    plt.savefig(outdir+'eres_'+mc['name']+'_sipm_fit.png')
    plt.close()

    pmt_fit = fit_energy(mc['pmts'].charge, bins_fit, fit_range_pmts)
    mc['pmt_eres'], mc['pmt_fwhm'], mc['pmt_mean'], mc['pmt_eres_err'], mc['pmt_fwhm_err'], mc['pmt_mean_err'] = get_fit_params(pmt_fit)
    print('PMTs -------')
    print_fit_energy(pmt_fit)
    plot_fit_energy(pmt_fit)
    plt.xlabel('charge [pes]')
    plt.title('Energy Resolution Fit, '+mc['name'])
    plt.savefig(outdir+'eres_'+mc['name']+'_pmt_fit.png')
    plt.close()
    print('')

if event_type == 'kr':
    event_str = '41.5 keV'
else:
    event_str = r'$Q_{\beta \beta}$'

def to_qbb(x):
    return x * np.sqrt(41./2458)

def back_tokr(x):
    return x / np.sqrt(41./2458)


fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['sipm_eres'] for mc in mc_size],
            [mc['sipm_eres_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
#fig.subplots_adjust(right=0.2)
ax.set_xlabel('SiPM pitch [mm]')
ax.set_ylabel(r'$E_{res}$ FWHM at '+event_str)
#secax.set_xlabel(r'$E_{res}$ FWHM at $Q_{\beta \beta}$')
ax.set_title('SiPM Energy Resolution')
plt.legend()
plt.savefig(outdir+'eres_'+'sipm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['pmt_eres'] for mc in mc_size],
            [mc['pmt_eres_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('SiPM pitch [mm]')
plt.title('PMT Energy Resolution')
plt.ylabel(r'$E_{res}$ FWHM at '+event_str)
plt.legend()
plt.savefig(outdir+'eres_'+'pmt.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['sipm_fwhm'] for mc in mc_size],
                [mc['sipm_fwhm_err'] for mc in mc_size],marker='o',
                label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('SiPM FWHM')
plt.legend()
plt.savefig(outdir+'eres_'+'sipm_fwhm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['pmt_fwhm'] for mc in mc_size],
            [mc['pmt_fwhm_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('PMT FWHM')
plt.legend()
plt.savefig(outdir+'eres_'+'pmt_fwhm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['sipm_mean'] for mc in mc_size],
            [mc['sipm_mean_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('SiPM Mean')
plt.legend()
plt.savefig(outdir+'eres_'+'sipm_mean.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.errorbar(pitches, [mc['pmt_mean'] for mc in mc_size],
            [mc['pmt_mean_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.ylabel('PMT Mean')
plt.xlabel('SiPM pitch [mm]')
plt.legend()
plt.savefig(outdir+'eres_'+'pmt_mean.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['sipm_eres'] for mc in mc_size],
            [mc['sipm_eres_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('Tracking Plane Coverage %')
plt.ylabel(r'$E_{res}$ FWHM at '+event_str)
plt.title('SiPM Energy Resolution')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'sipm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['pmt_eres'] for mc in mc_size],
            [mc['pmt_eres_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('Tracking Plane Coverage [mm]')
plt.legend()
plt.title('PMT Energy Resolution')
plt.ylabel(r'$E_{res}$ FWHM at '+event_str)
plt.savefig(outdir+'eres_coverage'+'pmt.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['sipm_fwhm'] for mc in mc_size],
            [mc['sipm_fwhm_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('Tracking Plane Coverage %')
plt.ylabel('SiPM FWHM')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'sipm_fwhm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['pmt_fwhm'] for mc in mc_size],
            [mc['pmt_fwhm_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('Tracking Plane Coverage %')
plt.ylabel('PMT FWHM')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'pmt_fwhm.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['sipm_mean'] for mc in mc_size],
            [mc['sipm_mean_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.xlabel('Tracking Plane Coverage %')
plt.ylabel('SiPM Mean')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'sipm_mean.png')
plt.close()

fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        coverages = [mc['coverage'] for mc in mc_size]
        plt.errorbar(coverages, [mc['pmt_mean'] for mc in mc_size],
            [mc['pmt_mean_err'] for mc in mc_size], marker='o',
            label=str(mc_size[0]['size'])+'mm SiPMs')
if event_type == 'kr':
    secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.ylabel('PMT Mean')
plt.xlabel('Tracking Plane Coverage %')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'pmt_mean.png')
plt.close()
