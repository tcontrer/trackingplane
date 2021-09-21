"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script holds functions used to open files for the tracking plane
simulations.
"""

def make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon=True):
    """
    Created dictionaries to hold all information on simulations and returns.
    Inputs:
        mcs_to_use ([str]): a list of strings corresponding to the mc sensor_name
        local (bool): describes wether testing localy or running on Harvard cluster
        event_type (str): 'kr' or 'qbb' for the type of event simulated
        teflon (bool): True if using simulations with teflon, False for no teflon
    Returns:
        mcs ([dict]): array of dictionaries
        outdir (str): directory for plots
        indir (str): directory for files to open
    """
    print("Creating dictionaries")
    all_mcs = {}
    all_mcs['s1p1'] =  {"size":1, "pitch":1, 'teflon':'no_teflon', 'name':'1mm SiPM, 1mm pitch', "dir":"s1mmp1mm"}
    all_mcs['s1p7'] = {"size":1, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 7mm pitch',"dir": "s1mmp7mm"}
    all_mcs['s1p15'] = {"size":1, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '1mm SiPM, 15mm pitch',"dir": "s1mmp15mm"}
    
    all_mcs['s13p13'] =  {"size":1.3, "pitch":1.3, 'teflon':'no_teflon', 'name':'1.3mm SiPM, 1.3mm pitch', "dir":"s1.3mmp1.3mm"}
    all_mcs['s13p7'] = {"size":1.3, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '1.3mm SiPM, 7mm pitch',"dir": "s1.3mmp7mm"}
    all_mcs['s13p15'] = {"size":1.3, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '1.3mm SiPM, 15mm pitch',"dir": "s1.3mmp15mm"}
    
    all_mcs['s3p3'] = {"size":3, "pitch":3, 'teflon':'no_teflon', 'name':'3mm SiPM, 3mm pitch', "dir":"s3mmp3mm"}
    all_mcs['s3p7'] = {"size":3, "pitch":7, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 7mm pitch',"dir": "s3mmp7mm"}
    all_mcs['s3p15'] = {"size":3, "pitch":15, 'teflon':'teflonhole_5mm', 'name': '3mm SiPM, 15mm pitch', "dir": "s3mmp15mm"}
    
    all_mcs['s6p6'] = {"size":6, "pitch":6,'teflon':'no_teflon', 'name':'6mm SiPM, 6mm pitch', "dir":"s6mmp6mm"}
    all_mcs['s6p15'] = {"size":6, "pitch":15, 'teflon':'teflonhole_8mm', 'name': '6mm SiPM, 15mm pitch', "dir": "s6mmp15mm"}

    mcs = [all_mcs[mc] for mc in mcs_to_use]
    if local:
        outdir = '/Users/taylorcontreras/Development/Research/trackingplane/'
        indir = outdir
        mcs = [all_mcs['s3p15']]
    else:
        if event_type == 'kr':
            outdir = '/n/home12/tcontreras/plots/trackingplane/krypton/'
            indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/"
        else:
            outdir = '/n/home12/tcontreras/plots/trackingplane/highenergy/'
            indir = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/output/highenergy/"

    for mc in mcs:
        if not teflon:
            mc['teflon'] = 'no_teflon'
        mc["files"] = [indir+mc['teflon']+'/'+mc['dir']+"/flex.kr83m."+str(i)+".nexus.h5"
                        for i in range(1,nfiles+1)]
        #print(mc['files'])
    return mcs, outdir, indir
