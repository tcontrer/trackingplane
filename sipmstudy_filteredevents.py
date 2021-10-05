"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyzes the number of photons seen by the SiPMs, ranking
the SiPMs by the ammount of photons it sees.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from open_files import make_mc_dictionaries

print("Starting")
nfiles = 1 # will fail if too few events
local = True
event_type = 'qbb'
teflon = False

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

def GoodEvents(event_particles, min_diff=30., r_cut=700., z_cut = 1500.):
    event_electrons = event_particles.loc[event_particles.particle_name=='e-']
    primary_electrons_event = event_electrons.loc[event_electrons.mother_id==0]
    centers = np.array([primary_electrons_event.final_x.values, primary_electrons_event.final_y.values, primary_electrons_event.final_z.values]).T
    blob_dist = np.array([abs(centers[0,i] - centers[1,i]) for i in range(len(centers[0]))]) - min_diff

    # Cut on number of blobs and distance between blobs
    if np.shape(centers)==(2,3) and np.all(blob_dist) > 0:
        rs = [np.sqrt(center[0]**2. + center[1]**2.) for center in centers]

        # Cut on x-y (r) and z positions away from edges
        if np.all(rs) < r_cut and np.all(centers[:,2]) < z_cut:
            return event_particles
    return

for mc in mcs:
    sipms_mean = np.array([])
    sipms_max = np.array([])
    for file in mc['files']:

        print('Running: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        # filter good events
        particles = pd.read_hdf(file, 'MC/particles')
        good_events = particles.groupby('event_id').apply(lambda grp: GoodEvents(grp))
        if not good_events.empty:
            good_events = good_events.event_id.drop_duplicates().values
            good_events = good_events[~np.isnan(good_events)].astype(int)
        else:
            continue

        # Sort to sum up all charges for each sipms
        sns_response = sns_response[sns_response.event_id.isin(good_events)]
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        sipms_mean = np.append(sipms_mean, sipm_response.groupby('event_id').apply(lambda grp: np.mean(grp.charge)))
        sipms_max = np.append(sipms_max, sipm_response.groupby('event_id').apply(lambda grp: np.max(grp.charge)))

    mc['sipms_mean'] = sipms_mean
    mc['sipms_max'] = sipms_max

    plt.hist(mc['sipms_max'])
    plt.xlabel('max charge [pes] / microsecond / event')
    plt.title(mc['name'])
    plt.yscale('log')
    plt.savefig(outdir+'edges_max_'+str(mc['name'])+'.png')
    plt.close()

    plt.hist(mc['sipms_mean'])
    plt.xlabel('mean charge [pes] / microsecond / event')
    plt.title(mc['name'])
    plt.yscale('log')
    plt.savefig(outdir+'edges_mean_'+str(mc['name'])+'.png')
    plt.close()

mcs_by_size = [[], [], []]
for mc in mcs:
    if mc['size'] == 1.3:
        mcs_by_size[0].append(mc)
        mc['r_max'] = (0,1500)
        mc['r_mean'] = (0,8)
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
        mc['r_max'] = (0, 10000)
        mc['r_mean'] = (0,25)
    elif mc['size'] == 6:
        mcs_by_size[2].append(mc)
        mc['r_max'] = (0, 35000)
        mc['r_mean'] = (0,60)

bins = 100
for mcs in mcs_by_size:
    bins_mean = 0
    for mc in mcs:
        plt.hist(mc['sipms_max'], label=mc['name'], range=mc['r_max'], bins=bins)
        bins_mean = max(bins_mean, mc['r_mean'][1])
    plt.xlabel('max charge [pes] / microsecond / event')
    plt.title(str(mc['size'])+'mm SiPMs')
    plt.yscale('log')
    plt.legend()
    plt.savefig(outdir+'edges_max_'+str(mc['size'])+'mm.png')
    plt.close()

    for mc in mcs:
        plt.hist(mc['sipms_mean'], label=mc['name'], range=mc['r_mean'], bins=bins_mean)
    plt.xlabel('mean charge [pes] / microsecond / event')
    plt.title(str(mc['size']) + 'mm SiPMs')
    plt.yscale('log')
    plt.legend()
    plt.savefig(outdir+'edges_mean_'+str(mc['size'])+'mm.png')
    plt.close()
