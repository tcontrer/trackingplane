"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the saturation of the SiPMs for a given max energy cut.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from open_files import make_mc_dictionaries

print("Starting")
nfiles = 500 # will fail if too few events
local = False
event_type = 'qbb'
teflon = False

mcs_to_use = ['s13p7', 's3p7', 's6p6']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon, new=True)
cuts = np.linspace(0, 50, 5)
for mc in mcs:

    if mc['size'] == 1 or mc['size'] == 1.3:
        big_cuts = np.linspace(0, 700, 10)
    elif mc['size'] == 3:
        big_cuts = np.linspace(0, 5000, 10)
    elif mc['size'] == 6:
        big_cuts = np.linspace(0, 20000, 10)
    mc['big_cuts'] = big_cuts

    num_unsat_by_cut = []
    num_events_unsat = []
    energy_by_cut = []
    nevents = 0
    for file in mc['files']:
        print('Running over: '+file)
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_positions = sns_positions.drop_duplicates(subset='sensor_id')

        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

        this_num_sat_by_cut = []
        #for cut in cuts:
        #    sat_sipms = sipm_response.groupby('event_id').apply(
        #        lambda grp: len(grp[grp.charge > cut])).values.mean()
        #    this_num_sat_by_cut.append(sat_sipms)
        #num_sat_by_cut.append(this_num_sat_by_cut)

        max_charges = sipm_response.groupby('event_id').apply(lambda grp: grp.charge.max())
        total_charge = sipm_response[['event_id', 'charge']].groupby('event_id').agg({'charge':'sum'})
        this_num_events_unsat = []
        this_energy_by_cut = []
        for cut in big_cuts:
            #print('cut',cut)
            this_num_events_unsat.append(len(max_charges[max_charges.values < cut]))
            unsat_response = sipm_response[['event_id', 'charge']][sipm_response.charge < cut]
            if unsat_response.empty:
                #print('unsat_response', 0.0)
                this_energy_by_cut.append(0.0)
            else:
                #print('unsat_response',unsat_response)
                #sat_response.loc[:,('charge')] = sat_response.charge - cut
                unsat_response = unsat_response.groupby('event_id').agg({"charge":"sum"})
                #print('summed unsat response', unsat_response)
                this_energy_by_cut.append((unsat_response / total_charge).mean())
        num_events_unsat.append(this_num_events_unsat)
        energy_by_cut.append(this_energy_by_cut)
        nevents += len(sipm_response.groupby('event_id'))
    #print('Num unsat: ', num_unsat_by_cut)
    #mc['num_sat_by_cut'] = np.array(num_sat_by_cut).sum(axis=0)/nfiles
    mc['num_events_unsat'] = np.array(num_events_unsat).sum(axis=0)/nfiles
    mc['energy_by_cut'] = np.array(energy_by_cut).sum(axis=0)/nfiles
    mc['nevents'] = nevents

mc_sizes = [[], [], []]
for mc in mcs:
    #print(mc['name'], mc['size'])
    if mc['size'] == 1 or mc['size'] == 1.3:
        mc_sizes[0].append(mc)
    elif mc['size'] == 3:
        mc_sizes[1].append(mc)
    elif mc['size'] == 6:
        mc_sizes[2].append(mc)
#mc_sizes = [mcs]
# FIXME: drop entries if empty (necessary for local use)
#print('MC sizes:',mc_sizes)
"""for mc_size in mc_sizes:
    print('mc size:', mc_size)
    for mc in mc_size:
        print('mc: ', mc['name'])
        plt.plot(cuts, mc['num_sat_by_cut'], label=str(mc['pitch'])+'mm pitch')
    plt.xlabel('Max charge [pes]')
    plt.ylabel('Instances of a Saturated SiPM')
    plt.title(str(mc['size'])+'mm SiPMs')
    plt.legend()
    plt.savefig(outdir+'sat_'+str(mc['size'])+'mm_inst.png')
    plt.close()

for mc_size in mc_sizes:
    for mc in mc_size:
        plt.plot(mc['big_cuts'], mc['num_events_sat'], label=str(mc['pitch'])+'mm pitch')
    plt.xlabel('Max Charge [pes]')
    plt.ylabel('Number of Events')
    plt.title('Saturation in '+str(mc['size'])+'mm SiPMs')
    plt.legend()
    plt.savefig(outdir+'sat_'+str(mc['size'])+'mm_numevents.png')
    plt.close()"""

for mc_size in mc_sizes:
    for mc in mc_size:
        plt.plot(mc['big_cuts'], np.array(mc['num_events_unsat'])/mc['nevents'],
                 label=str(mc['pitch'])+'mm pitch', marker='o')
    plt.xlabel('Max Charge [pes]')
    plt.ylabel('Unsaturated Events / Total Events')
    plt.ylim(-0.05,1.05)
    plt.xlim(0,mc['big_cuts'][-1])
    plt.title('Saturation in '+str(mc['size'])+'mm SiPMs')
    plt.legend()
    plt.savefig(outdir+'sat_'+str(mc['size'])+'mm_fracevents.png')
    plt.close()

for mc_size in mc_sizes:
    for mc in mc_size:
        plt.plot(mc['big_cuts'], mc['energy_by_cut'], label=str(mc['pitch'])+'mm pitch', marker='o')
    plt.xlabel('Max Charge [pes]')
    plt.ylabel('(Charge < Max Charge) / Total charge')
    plt.title(str(mc['size'])+'mm SiPMs')
    plt.ylim(-0.05,1.05)
    plt.xlim(0,mc['big_cuts'][-1])
    #plt.yscale('log')
    plt.legend()
    plt.savefig(outdir+'sat_'+str(mc['size'])+'mm_fracpes.png')
    plt.close()

for mc_size in mc_sizes:
    plt.plot(mc_size[0]['big_cuts'], mc_size[0]['num_events_unsat']/mc_size[0]['nevents'], label=mc_size[0]['name'], marker='o')
plt.xlabel('Max Charge [pes]')
plt.ylabel('Unsaturated Events / Total Events')
plt.ylim(-0.05,1.05)
plt.xlim(0,mc['big_cuts'][-1])
plt.legend()
plt.savefig(outdir+'sat__fracevents.png')
plt.close()

for mc_size in mc_sizes:
    plt.plot(mc_size[0]['big_cuts'], mc_size[0]['energy_by_cut'], label=mc_size[0]['name'], marker='o')
plt.xlabel('Max Charge [pes]')
plt.ylabel('(Charge < Max Charge) / Total charge')
plt.ylim(-0.05,1.05)
plt.xlim(0,mc['big_cuts'][-1])
#plt.yscale('log')
plt.legend()
plt.savefig(outdir+'sat_fracpes.png')
plt.close()

