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

print("Starting")
nfiles = 100 # will fail if too few events
local = False
event_type = 'qbb'

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
        mc["files"] = [indir+'teflonhole_5mm/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
        
    
for mc in mcs:
    
    sipms = pd.DataFrame()
    pmts = pd.DataFrame()
    for file in mc['files']:
        sns_response = pd.read_hdf(file, 'MC/sns_response')
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

    mc['sipms'] = sipms
    mc['pmts'] = pmts

    
for mc in mcs:
    bins_fit = 500
    if event_type == 'kr':
        fit_range_sipms = (np.min(mc['sipms'].charge), np.max(mc['sipms'].charge))
        fit_range_pmts = (np.min(mc['pmts'].charge), np.max(mc['pmts'].charge))
    else:
        fit_range_sipms = (np.mean(mc['sipms'].charge) - np.std(mc['sipms'].charge), np.mean(mc['sipms'].charge) + np.std(mc['sipms'].charge))
        fit_range_pmts = (np.mean(mc['pmts'].charge) - np.std(mc['pmts'].charge), np.mean(mc['pmts'].charge) + np.std(mc['pmts'].charge))

    sipm_fit = fit_energy(mc['sipms'].charge, bins_fit, fit_range_sipms)
    mc['sipm_eres'], mc['sipm_fwhm'], mc['sipm_mean'] = get_fit_params(sipm_fit)
    print_fit_energy(sipm_fit)
    plot_fit_energy(sipm_fit)
    plt.savefig(outdir+'eres_'+mc['dir']+'_sipm_fit.png')
    plt.close()

    pmt_fit = fit_energy(mc['pmts'].charge, bins_fit, fit_range_pmts)
    mc['pmt_eres'], mc['pmt_fwhm'], mc['pmt_mean'] = get_fit_params(pmt_fit)
    print_fit_energy(pmt_fit)
    plot_fit_energy(pmt_fit)
    plt.savefig(outdir+'eres_'+mc['dir']+'_pmt_fit.png')
    plt.close()
   
if event_type == 'kr':
    event_str = '41.5 keV'
else:
    event_str = r'$Q_{\beta \beta}$'

pitches = [mc['pitch'] for mc in mcs]
plt.plot(pitches, [mc['sipm_eres'] for mc in mcs], 'o')
plt.xlabel('SiPM pitch [mm]')
plt.ylabel(r'$E_{res}$ FWHM at '+event_str)
plt.title('SiPM Energy Resolution')
plt.savefig(outdir+'eres_'+'sipm.png')
plt.close()

plt.plot(pitches, [mc['pmt_eres'] for mc in mcs], 'o')
plt.xlabel('SiPM pitch [mm]')
plt.title('PMT Energy Resolution')
plt.ylabel(r'$E_{res}$ FWHM at '+event_str)
plt.savefig(outdir+'eres_'+'pmt.png')
plt.close()

plt.plot(pitches, [mc['sipm_fwhm'] for mc in mcs], 'o')
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('SiPM FWHM')
plt.savefig(outdir+'eres_'+'sipm_fwhm.png')
plt.close()

plt.plot(pitches, [mc['pmt_fwhm'] for mc in mcs], 'o')
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('PMT FWHM')
plt.savefig(outdir+'eres_'+'pmt_fwhm.png')
plt.close()

plt.plot(pitches, [mc['sipm_mean'] for mc in mcs], 'o')
plt.xlabel('SiPM pitch [mm]')
plt.ylabel('SiPM Mean')
plt.savefig(outdir+'eres_'+'sipm_mean.png')
plt.close()

plt.plot(pitches, [mc['pmt_mean'] for mc in mcs], 'o')
plt.ylabel('PMT Mean')
plt.xlabel('SiPM pitch [mm]')
plt.savefig(outdir+'eres_'+'pmt_mean.png')
plt.close()


                                       

