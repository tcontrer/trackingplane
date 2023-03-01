import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tables as tb

from invisible_cities.cities import components as cp
from invisible_cities.database import load_db

num_full_files = 3
num_fast_files = 3
outdir = '/n/home12/tcontreras/plots/trackingplane/highenergy/'

fast_file_dir = "/n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/0vbb/fast_simulations/detsim/20220217_dlopezgutierrez_1.3s15.00p/hdf5_files/"
fast_file_start = "flex_0vbb_fast_size1.3_pitch15.00."
fast_file_end = ".detsim.h5"
fast_files = [fast_file_dir + fast_file_start + str(i+1) + fast_file_end for i in range(num_fast_files)]

full_file_dir = "/n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/0vbb/20211207_tcontreras/buffy/teflon/s1.3mmp15mm/"
full_file_start = "flex.0vbb."
full_file_end = ".fullsim_buffy.h5"
full_files = [full_file_dir + full_file_start + str(i+1) + full_file_end for i in range(num_full_files)]

print(fast_files)
print(full_files)

# Gather detsim info (fast simulations)
detsim_data = cp.wf_from_files(fast_files, cp.WfType.mcrd)
fast_pmt_events = []
fast_sipm_events = []
try:
    while detsim_data:
        thisdata = next(detsim_data)
        fast_pmt_events.append(thisdata['pmt'])
        fast_sipm_events.append(thisdata['sipm'])
except StopIteration:
    pass

finally:
    del detsim_data

# Gather buffy info (full simulations)
buffy_data = cp.wf_from_files(full_files, cp.WfType.mcrd)
full_pmt_events = []
full_sipm_events = []
try:
    while buffy_data:
        thisdata = next(buffy_data)
        full_pmt_events.append(thisdata['pmt'])
        full_sipm_events.append(thisdata['sipm'])
except StopIteration:
    pass

finally:
    del buffy_data


fast_summed_sipms = np.sum(np.sum(fast_sipm_events, axis=1),axis=1)
full_summed_sipms = np.sum(np.sum(full_sipm_events, axis=1),axis=1)

plt.hist(fast_summed_sipms, bins=50, label='Fast Sims', range=(0,150000))
plt.hist(full_summed_sipms, bins=50, label='Full Sims', range=(0,150000))
plt.xlabel('Total Charge in SiPMs [pes]')
plt.legend()
plt.savefig(outdir+'fvf_charge.png')
