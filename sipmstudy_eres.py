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

from ic_functions import *

def Thresh_by_Event(group, dark_count):
    event = group.index.tolist()[0] #.event_id.max()
    thresh = dark_count.loc[event].dark_count
    return group[group.charge > thresh]

print("Starting")
nfiles = 1000 # will fail if too few events
local = False
event_type = 'qbb'

tp_area = np.pi * (984./2.)**2 # mm^2
dark_rate = {1:80./1000., 3: 450./1000., 6: 1800./1000.} # SiPM size: average dark rate per sipm (counts/microsecond)
if event_type == 'kr':
    event_time = 20. # microseconds
else:
    event_time = 100. # microseconds

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

        # Sum up all charges per event in sipms
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]
        #print('sipm_response before: ', sipm_response)
        #if not sipm_response.loc[sipm_response["time_bin"] >0].empty:
        #    sipm_response = sipm_response.loc[sipm_response["time_bin"] >0]
        #    pmt_response = pmt_response.loc[pmt_response["time_bin"] >0]
        #print('sipm_response after: ', sipm_response)

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
    #dark_count  = sipm_timing*dark_rate[mc['size']]
    #dark_count = dark_count.to_frame().rename(columns={0:'dark_count'})
    #sipms = this.apply(Thresh_by_Event, (dark_count))#.set_index('event_id') #.groupby('event_id')

    # Threshold based on dark noise
    #sipms = sipms[sipms.charge > dark_rate[mc['size']]*event_time]
    print(sipms)
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
    if mc['size'] == 1:
        mc_sizes[0].append(mc)
    elif mc['size'] == 3:
        mc_sizes[1].append(mc)
    elif mc['size'] == 6:
        mc_sizes[2].append(mc)
    
for mc in mcs:
    bins_fit = 50
    if event_type == 'kr':
        fit_range_sipms = (np.mean(mc['sipms'].charge)-np.std(mc['sipms'].charge), np.mean(mc['sipms'].charge)+np.std(mc['sipms'].charge))
        fit_range_pmts = (np.mean(mc['pmts'].charge)-np.std(mc['pmts'].charge), np.mean(mc['pmts'].charge)+np.std(mc['pmts'].charge))
    else:
        fit_range_sipms = (np.mean(mc['sipms'].charge) + np.std(mc['sipms'].charge)/2., np.mean(mc['sipms'].charge) + np.std(mc['sipms'].charge))
        fit_range_pmts = (np.mean(mc['pmts'].charge), np.mean(mc['pmts'].charge) + np.std(mc['pmts'].charge))

    #print(mc['dir']+': Average Dark count = '+str(mc['dark_count']))

    sipm_fit = fit_energy(mc['sipms'].charge, bins_fit, fit_range_sipms)
    mc['sipm_eres'], mc['sipm_fwhm'], mc['sipm_mean'] = get_fit_params(sipm_fit)
    print(mc['name'])
    print('SiPMs')
    print_fit_energy(sipm_fit)
    plot_fit_energy(sipm_fit)
    plt.xlabel('charge [pes]')
    plt.title('Energy Resolution Fit, '+mc['name'])
    plt.savefig(outdir+'eres_'+mc['name']+'_sipm_fit.png')
    plt.close()

    pmt_fit = fit_energy(mc['pmts'].charge, bins_fit, fit_range_pmts)
    mc['pmt_eres'], mc['pmt_fwhm'], mc['pmt_mean'] = get_fit_params(pmt_fit)
    print('PMTs')
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
    return x / np.sqrt(2.4)

def back_tokr(x):
    return x * np.sqrt(2.4)


fig, ax = plt.subplots()
for mc_size in mc_sizes:
    if mc_size:
        pitches = [mc['pitch'] for mc in mc_size]
        plt.plot(pitches, [mc['sipm_eres'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(pitches, [mc['pmt_eres'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(pitches, [mc['sipm_fwhm'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(pitches, [mc['pmt_fwhm'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(pitches, [mc['sipm_mean'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(pitches, [mc['pmt_mean'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['sipm_eres'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['pmt_eres'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['sipm_fwhm'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['pmt_fwhm'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['sipm_mean'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
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
        plt.plot(coverages, [mc['pmt_mean'] for mc in mc_size], 'o', label=str(mc_size[0]['size'])+'mm SiPMs')
secax = ax.secondary_yaxis('right', functions=(to_qbb, back_tokr))
plt.ylabel('PMT Mean')
plt.xlabel('Tracking Plane Coverage %')
plt.legend()
plt.savefig(outdir+'eres_coverage'+'pmt_mean.png')
plt.close()
