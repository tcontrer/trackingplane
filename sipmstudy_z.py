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
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from open_files import make_mc_dictionaries

print("Starting")
nfiles = 1 # will fail if too few events
local = True
event_type = 'kr'
teflon = False

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)

def FindFinalz(grp):
    final_z = grp[particles.mother_id==0][particles.particle_name=='e-'].final_z
    if not final_z.empty:
        return final_z.values[0]
    return

for mc in mcs:
    sipm_zmap = pd.DataFrame()

    for file in mc['files']:

        print('Running: '+file)
        try:
            sns_response = pd.read_hdf(file, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file)
            continue

        # Sort to sum up all charges for each sipms
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

        # Summed sipm energy per event
        response_perevent_sipm = sipm_response.groupby('event_id')
        summed_charges_byevent_sipm = response_perevent_sipm.agg({"charge":"sum"})

        # Find z position
        particles = pd.read_hdf(file, 'MC/particles')
        z_map = particles.groupby('event_id').apply(lambda grp: FindFinalz(grp)).dropna()
        z_map = pd.DataFrame({'event_id':z_map.index, 'z':z_map.values}).set_index('event_id')
        sipm_zmap = sipm_zmap.append(pd.concat([summed_charges_byevent_sipm, z_map], axis=1))

    mc['sipm_zmap'] = sipm_zmap

    plt.hist2d(sipm_zmap.z, sipm_zmap.charge, bins=[50,50], cmin=1)
    plt.xlabel('z [mm]')
    plt.ylabel('charge [pes]')
    plt.title(mc['name'])
    plt.colorbar()
    plt.savefig(outdir+'zmap_'+mc['dir']+'.png')
