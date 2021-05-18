import pandas as pd
import matplotlib.pyplot as plt


print("Starting")
nfiles = 100 # need this many so it doesn't fail due to being too few files and the later stuff is empty
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
for mc in mcs:
    print("Looping in mcs")
    top_sipms = pd.DataFrame()

    for file in mc["files"]:
        print("Looping files in mc")
        sns_response = pd.read_hdf(file, 'MC/sns_response')

        # Sort to sum up all charges for each sipms
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

        top_sipms = top_sipms.append(sipm_response.groupby('event_id',as_index=False).apply(lambda grp: grp.nlargest(10,'charge')))
        
    top_sipms_by_event = top_sipms.groupby('event_id')
    mc["top_sipms"] = [top_sipms_by_event.apply(lambda grp: grp.iloc[i]) for i in range(0,10)]

print("Plotting")
# Plot each i-th sipm for each mc
for mc in mcs:
    for i in range(0,10):
        plt.hist(mc['top_sipms'][i]['charge'], bins=50, range=(0,250))
        plt.xlabel('charge [pes]')
        plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch, '+str(i)+' largest sipm signal per event')
        plt.savefig(outdir+mc['dir']+"_"+str(i)+"largest_sipm.png")
        plt.close()

# Plot top 5 sipms for each mc
for mc in mcs:
    for i in range(0,5):
        plt.hist(mc['top_sipms'][i]['charge'], alpha=0.5, bins=50, range=(0,250), label=str(i))
    plt.xlabel('charge [pes]')
    plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(mc['pitch'])+' pitch')
    plt.legend()
    plt.savefig(outdir+mc['dir']+"largests_5sipms_comp.png")
    plt.close()

# Plot top i-th sipm across mcs
for i in range(0,10):
    for mc in mcs:
        plt.hist(mc['top_sipms'][i]['charge'], alpha=0.5, bins=50, range=(0,250), label=str(mc['size'])+" sipms, "+str(mc['pitch'])+" pitch")
    plt.xlabel('charge [pes]')
    plt.title('NEXT-100, 3mmx3mm SiPMs, '+str(i)+" largest sipm signal per event")
    plt.legend()
    plt.savefig(outdir+str(i)+"largest_sipm_comp.png")
    plt.close()
