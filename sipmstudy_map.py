import pandas as pd
import matplotlib.pyplot as plt

def hist(*args, **kwargs):
    """
    Create a figure and then the histogram
    """
    create_new_figure(kwargs)

    y, x, p = plt.hist(*args, **kwargs)
    return y, shift_to_bin_centers(x), p


def hist2d(*args, **kwargs):
    """
    Create a figure and then the histogram
    """
    create_new_figure(kwargs)

    z, x, y, p = plt.hist2d(*args, **kwargs)
    return z, shift_to_bin_centers(x), shift_to_bin_centers(y), p

def hist2d_profile(x, y, z, nbinx, nbiny, xrange, yrange, **kwargs):
    """
    Create a profile 2d of the data and plot it as an histogram.
    """
    x, y, z, ze = fitf.profileXY(x, y, z, nbinx, nbiny, xrange, yrange)
    plot_output = display_matrix(x, y, z, **kwargs)
    return ((x, y, z, ze), *plot_output)

def display_matrix(x, y, z, mask=None, **kwargs):
    """
    Display the matrix z using the coordinates x and y as the bin centers.
    """
    nx = x = np.size(x)
    ny = np.size(y)

    dx = (np.max(x) - np.min(x)) / nx
    dy = (np.max(y) - np.min(y)) / ny

    x_binning = np.linspace(np.min(x) - dx, np.max(x) + dx, nx + 1)
    y_binning = np.linspace(np.min(y) - dy, np.max(y) + dy, ny + 1)

    x_ = np.repeat(x, ny)
    y_ = np.tile  (y, nx)
    z_ = z.flatten()

    if mask is None:
        mask = np.ones_like(z_, dtype=bool)
    else:
        mask = mask.flatten()
    h  = hist2d(x_[mask], y_[mask], (x_binning,
                                     y_binning),
                weights = z_[mask],
                **kwargs)
    return h, plt.colorbar()

def create_new_figure(kwargs):
    if kwargs.setdefault("new_figure", True):
        plt.figure()
    del kwargs["new_figure"]

def labels(xlabel, ylabel, title=""):
    """
    Set x and y labels.
    """
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title ( title)



print("Starting")
nfiles = 10 # need this many so it doesn't fail due to being too few files and the later stuff is empty
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
s3p6 = {"size":3, "pitch":6, "dir": dirname6, "files":[dirname6+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p7 = {"size":3, "pitch":7, "dir": dirname7, "files":[dirname7+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p8 = {"size":3, "pitch":8, "dir": dirname8, "files":[dirname8+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p9 = {"size":3, "pitch":9, "dir":dirname9, "files":[dirname9+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p10 = {"size":3, "pitch":10, "dir":dirname10, "files":[dirname10+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
s3p15 = {"size":3, "pitch":15, "dir":dirname15, "files":[dirname15+"/flex.kr83m."+str(i)+".nexus.h5" for i in range(1,nfiles)]}
mcs = [s3p6, s3pT, s3p7, s3p8, s3p9, s3p10, s3p15]

# Loop over the simulations and collect the sensor info by storing in the mc dict
print("About to loop")
for mc in mcs:
    print("Looping in mcs")
    pmt_map = pd.DataFrame()
    sipm_map = pd.DataFram()

    for file in mc["files"]:
        print("Looping files in mc")
        # Get all sensor responses and all the sensor positions
        sns_response = pd.read_hdf(this_dir+file_name, 'MC/sns_response')
        sns_positions = pd.read_hdf(this_dir+file_name, 'MC/sns_positions')

        # Sort to get the sipm positions
        sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
        sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

        # Create separate dataframes for the sipm and pmt response
        sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
        sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]
        pmt_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] < 60]

        # Summed pmt energy per event
        response_perevent_pmt = pmt_response.groupby('event_id')
        summed_charges_byevent_pmt = response_perevent_pmt.agg({"charge":"sum"})

        # Summed sipm energy per event
        response_perevent_sipm = sipm_response.groupby('event_id')
        summed_charges_byevent_sipm = response_perevent_sipm.agg({"charge":"sum"})

        # Position of the event(sipm with the max charge)
        idx = sipm_response.groupby(['event_id'])['charge'].transform(max) == sipm_response['charge']
        max_sipms = sipm_response[idx].sort_values('sensor_id').set_index('sensor_id')
        new_max_sipm_positions = sipm_positions.set_index('sensor_id')
        this = new_max_sipm_positions.loc[max_sipms.index.values.tolist()]
        event_map = pd.concat([max_sipms.loc[:,'event_id'],this.loc[:,['x','y','z']]], axis=1).set_index('event_id').sort_values(by='event_id')

        pmt_map.append(pd.concat([summed_charges_byevent_pmt,event_map],axis=1))
        sipm_map.append(pd.concat([summed_charges_byevent_sipm,event_map],axis=1))

    mc["pmt_map"] = pmt_map
    mc["sipm_map"] = sipm_map

nbins = 500/10
h = hist2d(sipm_map.x, sipm_map.y, (nbins, nbins), weights = sipm_map.charge)
labels("X [mm]", "Y [mm]", "SiPMs Light Distribution \n (NEXT-100, 6mm sipms, 10mm pitch)")
plt.savefig(this_dir+'sipm_kr_map.png')

h2 = hist2d(pmt_map.x, pmt_map.y, (nbins, nbins), weights = pmt_map.charge)
labels("X [mm]", "Y [mm]", "PMTs Light Distribution \n (NEXT-100)")
plt.savefig(this_dir+'pmt_kr_map.png')
