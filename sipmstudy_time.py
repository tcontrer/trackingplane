import pandas as pd
import matplotlib.pyplot as plt

print("Starting")
nfiles = 100
outdir = '/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-analysis/positions_random/'
indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/teflonhole_5mm/"
dirname6 = "s3mmp6mm"
dirname7 = "s3mmp7mm"
dirname8 = "s3mmp8mm"
dirname9 = "s3mmp9mm"
dirname10 = "s3mmp10mm"
dirname15 = "s3mmp15mm"


# Create dictionary to hold run info
print("Creating dictionaries")
s3p6 = {"size":3, "pitch":6, "dir": dirname6, "files":[indir+dirname6+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p7 = {"size":3, "pitch":7, "dir": dirname7, "files":[indir+dirname7+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p8 = {"size":3, "pitch":8, "dir": dirname8, "files":[indir+dirname8+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p9 = {"size":3, "pitch":9, "dir":dirname9, "files":[indir+dirname9+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p10 = {"size":3, "pitch":10, "dir":dirname10, "files":[indir+dirname10+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p15 = {"size":3, "pitch":15, "dir":dirname15, "files":[indir+dirname15+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
mcs = [s3p6, s3p7, s3p8, s3p9, s3p10, s3p15]

# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
pmt_time_binning = .025 # microseconds (25ns)
sipm_time_binning = 1.0 # microseconds
for mc in mcs:
    print("Looping in mcs")
    sipm_timing = pd.DataFrame()
    pmt_timing = pd.DataFrame()

    for file in mc["files"]:
        print("Looping files in mc")
        # Get all sensor responses and all the sensor positions
        sns_response = pd.read_hdf(file, 'MC/sns_response')
        sns_positions = pd.read_hdf(file, 'MC/sns_positions')
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]

        pmt_timing = pmt_timing.append(pmt_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()))
        sipm_timing = sipm_timing.append(sipm_response.groupby(['event_id']).apply(lambda group: group['time_bin'].max() - group['time_bin'].min()))

    mc["pmt_times"] = pmt_timing
    mc['sipm_times'] = sipm_timing

print("Plotting")
for mc in mcs:
    plt.hist(mc["pmt_times"], bins=50, range=(0,2000))
    plt.xlabel('Event width by PMTs [microseconds]')
    plt.title('NEXT_100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.savefig(outdir+mc['dir']+"_pmt_times".png")
    plt.close()

for mc in mcs:
    plt.hist(mc["sipm_times"], bins=50, range=(0,2000))
    plt.xlabel('Event width by SiPMs [microseconds]')
    plt.title('NEXT_100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.savefig(outdir+mc['dir']+"_sipm_times".png")
    plt.close()
