import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from mc_io_functions import load_mc_particles
from mc_io_functions import load_mc_hits
from mc_io_functions import load_mc_sensor_response

from invisible_cities.core.core_functions  import shift_to_bin_centers
from invisible_cities.core                 import fit_functions as fitf
#from invisible_cities.icaro.hst_functions import hist
#from invisible_cities.icaro.hst_functions import hist2d
#from invisible_cities.icaro.hst_functions import hist2d_profile
#from invisible_cities.icaro.hst_functions import labels

nfiles = 1
dirname = "/n/holystore01/LABS/guenette_lab/Users/tcontreras/nexus-production/test/"
files = [dirname+"flex.kr83m."+str(i)+".nexus.h5" for i in range(0,nfiles)]


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

sns_response = pd.read_hdf(files[0], 'MC/sns_response')
sns_positions = pd.read_hdf(files[0], 'MC/sns_positions')

sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]

sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >11]
response_byid = sipm_response.groupby('sensor_id')
summed_charges = response_byid.agg({"charge":"sum"}) 

new_sipm_positions = sipm_positions.set_index('sensor_id')

new_df = pd.concat([new_sipm_positions.iloc[:,1:5], summed_charges], axis=1)

# Plot sipm positions
XYrange       =  -500, 500
#hist2d(sipm_positions.x, sipm_positions.y, (25,25), [XYrange, XYrange])
plt.plot(sipm_positions.x, sipm_positions.y, ".")
plt.xlim(-50,50)
plt.ylim(-50,50)
plt.savefig("sipm_positions.png")
plt.close()

# Plot SiPM light distribution
hist2d_profile(new_df.x, new_df.y, new_df.charge, 25,  25, XYrange, XYrange)
plt.colorbar().set_label("total charge")
labels("X [mm]", "Y [mm]", "SiPMs Light Distribution \n (NEW.Kr83m, 100 events)")
plt.savefig("sipm_lightdistr.png")

