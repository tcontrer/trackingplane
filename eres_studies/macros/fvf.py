import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tables as tb

from invisible_cities.cities import components as cp
import invisible_cities.database.load_db
from invisible_cities.reco import xy_algorithms as xya

num_files = 101
data_dir = '/Users/taylorcontreras/Development/Research/trackingplane/data/reduced/'
fast_sims = sorted(glob.glob(fast_dir+'/*'))
full_sims = sorted(glob.glob(full_dir+'/*'))
database = invisible_cities.database.load_db.DataSiPM('flexs13p15')

sipm_xs    = database.X.values
sipm_ys    = database.Y.values
sipm_xys   = np.stack((sipm_xs, sipm_ys), axis=1)

dcuts = [20, 100, 500, 1000]
dcharges = []
for dcut in dcuts:
    nfiles = 100
    nevents = 100
    dcharge = []
    for file in range(nfiles):
        fast_data = pd.read_hdf(fast_sims[file], 'SiPM/Waveforms')
        full_data = pd.read_hdf(full_sims[file], 'SiPM/Waveforms')
        for evt in range(nevents):
            event = fast_data[fast_data.event_id==evt]
            if len(event) > 0:
                max_sipm = int(event[event.charge==event.charge.max()].sensor_id.tolist()[0])
                within_lm_radius = xya.get_nearby_sipm_inds(sipm_xys[int(max_sipm)-1000], dcut, sipm_xys)
                sipms_within_lm = event[event.sensor_id.isin(within_lm_radius+1000)]
                charge_fast = sipms_within_lm.charge.sum()
                #print(evt, max_sipm, len(sipms_within_lm), charge_fast, dcut)

                event = full_data[full_data.event_id==evt]
                max_sipm = int(event[event.charge==event.charge.max()].sensor_id.tolist()[0])
                within_lm_radius = xya.get_nearby_sipm_inds(sipm_xys[int(max_sipm)-1000], dcut, sipm_xys)
                sipms_within_lm = event[event.sensor_id.isin(within_lm_radius+1000)]
                #print(dcut)
                #print(sipms_within_lm)
                charge_full = sipms_within_lm.charge.sum()

                dcharge.append(charge_fast/charge_full)
    dcharges.append(dcharge)

plt.hist(dcharges[0], bins=25, range=(0.5,1.5), label='d < '+str(dcuts[0]), alpha=0.5)
plt.hist(dcharges[-1], bins=25, range=(0.5,1.5), label='d < '+str(dcuts[-1]), alpha=0.5)
plt.xlabel('Fast Sim / Full Sim [pes]')
plt.legend()
plt.show()