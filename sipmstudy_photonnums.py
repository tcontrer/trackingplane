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


print("Starting")
nfiles = 100 # will fail if too few events
local = False
event_type = 'kr'
num_sipms = 5

# Create dictionary to hold run info
print("Creating dictionaries")
s1p1 = {"size":1, "pitch":1, 'teflon':'no_teflon', 'name':'1mm SiPM, full coverage', "dir":"fullcoverage", 'extra_dir':'/s1mmp1mm'}
s1p7 = {"size":1, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 7mm pitch',"dir": "s1mmp7mm"}
s1p15 = {"size":1, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 15mm pitch',"dir": "s1mmp15mm"}
s13p13 = {"size":1.3, "pitch":1.3, 'teflon':'no_teflon', 'name':'1.3mm SiPM, full coverage', "dir":"fullcoverage", 'extra_dir':'/s1.3mmp1.3mm'}
s13p7 = {"size":1.3, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '1.3mm SiPM, 7mm pitch',"dir": "s1.3mmp7mm"}
s13p15 = {"size":1.3, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '1.3mm SiPM, 15mm pitch',"dir": "s1.3mmp15mm"}
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
s6p15nt = {"size":6, "pitch":15, 'teflon':'no_teflon', 'name': '6mm SiPM, 15mm pitch, no teflon', "dir": "s6mmp15mm"}
s1p7nt = {"size":1, "pitch":7, 'teflon':'no_teflon', 'name': '1mm SiPM, 7mm pitch, no teflon',"dir": "s1mmp7mm"}
s1p15nt = {"size":1, "pitch":15, 'teflon':'no_teflon', 'name': '1mm SiPM, 15mm pitch, no teflon',"dir": "s1mmp15mm"}
s3p15nt = {"size":3, "pitch":15, 'teflon':'no_teflon', 'name': '3mm SiPM, 15mm pitch, no teflon', "dir": "s3mmp15mm"}
s6p7nt = {"size":6, "pitch":7, 'teflon':'no_teflon', 'name': '6mm SiPM, 7mm pitch, no teflon',"dir": "s6mmp7mm"}


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

    mcs = [s13p13, s13p7, s13p15, s3p3, s3p7, s3p15, s6p6, s6p15]

for mc in mcs:
    if mc['dir'] == "fullcoverage":
        mc["files"] = [indir+mc['dir']+mc['extra_dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
    else:
        if not local:
            mc["files"] = [indir+'teflonhole_5mm/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]
        else:
            mc["files"] = [indir+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles+1)]

# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    top_sipms = pd.DataFrame()


for mc in mcs:
    this_num_sipms = num_sipms
    top_sipms = pd.DataFrame()
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

        #sipm_response_byevent = sipm_response.groupby('event_id',as_index=False)
        #num_sipms_byevent = sipm_response.groupby('event_id',as_index=False).apply(lambda grp: len(grp.sensor_id.values))
        #this_num_sipms = min(num_sipms_byevent.min(), this_num_sipms)
        #these_top_sipms = sipm_response_byevent.apply(lambda grp: grp.nlargest(this_num_sipms,'charge'))

        sipm_response_byevent = sipm_response.groupby('event_id',as_index=False)
        num_sipms_byevent = sipm_response.groupby('event_id').apply(lambda grp: len(grp.sensor_id.values))
        events_with_enough_sipms = num_sipms_byevent[num_sipms_byevent.values >= num_sipms].index
        sipm_response = sipm_response[sipm_response.event_id.isin(events_with_enough_sipms)]
        sipm_response_byevent =sipm_response.groupby('event_id',as_index=False)
        these_top_sipms = sipm_response_byevent.apply(lambda grp: grp.nlargest(this_num_sipms,'charge'))

        top_sipms = top_sipms.append(these_top_sipms)

    mc['top_sipms'] = top_sipms
    mc['num_sipms'] = this_num_sipms

print("Plotting")
# Plot each i-th sipm for each mc
mcs_by_size = [[], [], []]
for mc in mcs:
    if mc['size'] == 1 or mc['size'] == 1.3:
        mcs_by_size[0].append(mc)
    elif mc['size'] == 3:
        mcs_by_size[1].append(mc)
    elif mc['size'] == 6:
        mcs_by_size[2].append(mc)
print(mcs_by_size)
for mc in mcs:
    for i in range(0,mc['num_sipms']):
        plt.hist(mc['top_sipms'].groupby('event_id').apply(lambda grp: grp.iloc[i]).charge)
        plt.xlabel('charge [pes]')
        plt.title('NEXT-100, '+mc['name']+', '+str(i+1)+' largest sipm signal per event')
        plt.savefig(outdir+'photonnums_'+mc['name']+"_"+str(i+1)+"largest_sipm.png")
        plt.close()

# Plot top 5 sipms for each mc
for mc in mcs:
    r=(0,100)
    if event_type == 'kr':
        if mc['size'] == 1 or mc['size'] == 1.3:
            r = (0, 50)
        elif mc['size'] == 3:
            r = (0,500)
        elif mc['size'] == 6:
            r = (0, 2300)
    else:
        if mc['size'] == 1 or mc['size'] == 1.3:
            r = (0, 400)
        elif mc['size'] == 3:
            r = (0,7000)
        elif mc['size'] == 6:
            r = (0, 7000)

    for i in range(0,mc['num_sipms']):
        plt.hist(mc['top_sipms'].groupby('event_id').apply(lambda grp: grp.iloc[i]).charge, alpha=0.5, label=str(i+1), bins=50, range=r)
    plt.xlabel('charge [pes]')
    plt.title('NEXT-100, '+mc['name'])
    plt.legend()
    plt.savefig(outdir+'photonnums_'+mc['name']+"largests_5sipms_comp.png")
    plt.close()

# Plot top i-th sipm across mcs
for mc_size in mcs_by_size:
    print('Running over size: ', mc_size)
    #sizes = [mc['num_sipms'] for mc in mc_size]
    #sizes.append(num_sipms)
    #num_sipms = min(sizes)

    if not mc_size:
        continue
    for i in range(0, num_sipms):
        print('Running over sipm: ', i)
        for mc in mc_size:
            print('Running over mc: ', mc)

            if event_type == 'kr':
                if mc['size'] == 1 or mc['size'] == 1.3:
                    r = (0, 50)
                elif mc['size'] == 3:
                    r = (0,500)
                elif mc['size'] == 6:
                    r = (0, 2300)
            else:
                if mc['size'] == 1 or mc['size'] == 1.3:
                    r = (0, 400)
                elif mc['size'] == 3:
                    r = (0,7000)
                elif mc['size'] == 6:
                    r = (0, 22500)

            plt.hist(mc['top_sipms'].groupby('event_id').apply(lambda grp: grp.iloc[i]).charge, alpha=0.5, label=mc['name'], bins = 50, range=r)
        plt.xlabel('charge [pes]')
        plt.title('NEXT-100, '+str(mc['size'])+'mm SiPMs, '+str(i)+" largest sipm signal per event")
        plt.legend()
        plt.savefig(outdir+'photonnums_'+str(mc['size'])+'sipm_'+str(i)+"largest_sipm_comp.png")
        plt.close()
