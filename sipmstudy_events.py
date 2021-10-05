"""
Written by: Taylor Contreras, taylorcontreras@g.harvard.edu

This script uses output from the NEXT simulation software NEXUS,
and analyze blob shapes and energy event by event. Events must have
two blobs that are spatially separate. Blob 1 is the blob with the
largest energy.
"""

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from open_files import make_mc_dictionaries

print("Starting")
nfiles = 10
local = False
event_type = 'qbb'
teflon = False

mcs_to_use = ['s13p13', 's13p7', 's13p15', 's3p3', 's3p7', 's3p15', 's6p6', 's6p15']
mcs, outdir, indir = make_mc_dictionaries(mcs_to_use, local, nfiles, event_type, teflon)
print("made dirs")
def GetPeakInfo(event_response, mc_name):
    event_id = int(event_response.event_id.values[0])
    time_bins = event_response.time_bin.drop_duplicates().sort_values()
    plt.hist(time_bins, bins=100)
    plt.xlabel('Time bins [microseconds]')
    plt.title('Event '+str(event_id))
    #plt.show()
    plt.savefig(outdir+"event"+str(event_id)+"_"+mc_name+"timebins.png")
    plt.close()

    # Splits times into groups (peaks) to get blobs
    peaks = split_in_peaks(time_bins, 1)

    i = 1
    print('Event '+str(event_id))
    for peak_timebins in peaks:
        thispeak_charges = event_response.loc[event_response.time_bin.isin(peak_timebins)].drop_duplicates()

        summed_event = thispeak_charges.groupby('sensor_id').agg({'charge':'sum'}).reset_index()
        these_sipm_positions = sipm_positions.loc[sipm_positions.sensor_id.isin(summed_event.sensor_id.values)]
        sensor_positions_rep = these_sipm_positions.reindex(these_sipm_positions.index.repeat(summed_event.groupby('sensor_id').sensor_id.count().values))
        summed_event = summed_event.merge(sensor_positions_rep)
        fig, ax = plt.subplots()
        h = ax.hist2d(summed_event.x, summed_event.y, weights=summed_event.charge, bins=[50,50], cmin=1)
        fig.colorbar(h[3], ax=ax)
        ax.set_title('Event '+str(event_id)+', Charge in peak '+str(i))
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')
        #plt.show()
        fig.savefig(outdir+"event"+str(event_id)+"_"+mc_name+"_peak"+str(i)+"xyresponse.png")
        plt.close()

        max_sipm = thispeak_charges.loc[thispeak_charges.charge == thispeak_charges.charge.max()].sensor_id.values[0]
        max_sipm_response = thispeak_charges.loc[thispeak_charges.sensor_id == max_sipm]
        plt.plot(max_sipm_response.time_bin, max_sipm_response.charge, 'o')
        plt.title('Event '+str(event_id)+', Peak '+str(i)+', Maximum SiPM Response')
        plt.xlabel('Time bins [microseconds]')
        plt.ylabel('[pes]')
        #plt.show()
        plt.savefig(outdir+"event"+str(event_id)+"_"+mc_name+"_peak"+str(i)+"maxsipm.png")
        plt.close()

        width = thispeak_charges.time_bin.values.max() - thispeak_charges.time_bin.values.min()

        print('    Peak '+str(i))
        print('        Total charge = '+str(thispeak_charges.charge.sum()))
        print('        Max charge per time bin = '+str(thispeak_charges.charge.max()))
        print('        Width = '+str(width))

        i += 1

def GetBlobDensity(event_hits, centers, mc_name, rmax = 30., num_r = 100):
    event_id = int(event_hits.event_id.values[0])
    rs = np.linspace(1.0 ,rmax, num_r)
    blob_energies1 = []
    blob_energies2 = []
    for r in rs:
        blob1 = InsideBlob(event_hits, centers[0], r)
        blob2 = InsideBlob(event_hits, centers[1], r)
        blob_energies1.append(blob1.energy.sum())
        blob_energies2.append(blob2.energy.sum())

    # Name blob with largest energy 'blob 1'
    maxes = [max(blob_energies1), max(blob_energies2)]
    max_blob = np.where(maxes==max(maxes))
    if max_blob==0:
        name1 = 'blob 1'
        name2 = 'blob 2'
    else:
        name1 = 'blob 2'
        name2 = 'blob 1'

    #plt.plot(rs/10., np.array(blob_energies1)*10000/((4*np.pi*rs**3.)/3.), label=name1)
    #plt.plot(rs/10., np.array(blob_energies2)*10000/((4*np.pi*rs**3.)/3.), label=name2)
    #plt.legend()
    #plt.xlabel('Blob radius [cm]')
    #plt.ylabel('Blob energy density [keV/cm3]')
    #plt.title('Event '+str(event_id))
    #plt.yscale('log')
    #plt.show()
    #plt.savefig(outdir+"event"+str(event_id)+"_"+mc_name+"blob_density.png")
    #plt.close()


    plt.plot(rs, blob_energies1, label=name1)
    plt.plot(rs, blob_energies2, label=name2)
    plt.legend()
    plt.xlabel('Blob radius [mm]')
    plt.ylabel('Blob energy [MeV]')
    plt.title('Event '+str(event_id))
    #plt.yscale('log')
    #plt.show()
    plt.savefig(outdir+"event"+"_"+mc_name+str(event_id)+"blob_energy.png")
    plt.close()

def GoodBlobs(event_particles, min_diff=30.):
    event_electrons = event_particles.loc[event_particles.particle_name=='e-']
    primary_electrons_event = event_electrons.loc[event_electrons.mother_id==0]
    centers = np.array([primary_electrons_event.final_x.values, primary_electrons_event.final_y.values, primary_electrons_event.final_z.values]).T
    if len(centers) > 1 and np.all((np.array([abs(centers[0,i] - centers[1,i]) for i in range(len(centers[0]))]) - min_diff) > 0):
        return event_particles
    return

def split_in_peaks(indices, stride):
    where = np.where(np.diff(indices) > stride)[0]
    return np.split(indices, where + 1)

def InsideBlob(hit, center, blob_r = 20.):
    r = np.sqrt((center[0]-hit.x)**2. + (center[1] - hit.y)**2. + (center[2] - hit.z)**2.)#.values[0]
    return hit[r < blob_r]

for mc in mcs:
    for file_name in mc['files']:

        print('Running: '+file_name)
        try:
            sns_response = pd.read_hdf(file_name, 'MC/sns_response')
        except:
            print("Couldn't open file: "+file_name)
            continue

        # filter good events
        particles = pd.read_hdf(file_name, 'MC/particles')
        good_events = particles.groupby('event_id').apply(lambda grp: GoodBlobs(grp))
        if not good_events.empty:
            good_events = good_events.event_id.drop_duplicates().values
            good_events = good_events[~np.isnan(good_events)].astype(int)

            sns_positions = pd.read_hdf(file_name, 'MC/sns_positions')
            # Getting sensor info
            sns_pos_sorted = sns_positions.sort_values(by=['sensor_id'])
            sipm_positions = sns_pos_sorted[sns_pos_sorted["sensor_name"].str.contains("SiPM")]
            sns_response_sorted = sns_response.sort_values(by=['sensor_id'])
            sipm_response = sns_response_sorted.loc[sns_response_sorted["sensor_id"] >999]

            hits = pd.read_hdf(file_name, 'MC/hits')
            for event_id in good_events:

                # Plot entire track
                event_hits = hits[hits.event_id==event_id]
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                p = ax.scatter(event_hits.x, event_hits.y, event_hits.z, c=event_hits.energy, alpha=0.3, cmap='viridis')
                cb = fig.colorbar(p, ax=ax)
                cb.set_label('Energy (keV)')
                ax.set_xlabel('x (mm)')
                ax.set_ylabel('y (mm)')
                ax.set_zlabel('z (mm)')
                ax.set_title('Hits for event '+str(event_id))
                #plt.show()
                plt.savefig(outdir+"event"+str(event_id)+"_"+mc['dir']+"_track.png")
                plt.close()

                event_response = sipm_response[sipm_response.event_id==event_id]
                GetPeakInfo(event_response, mc['dir'])

                event_particles = particles[particles.event_id==event_id]
                event_electrons = event_particles.loc[event_particles.particle_name=='e-']
                primary_electrons_event = event_electrons.loc[event_electrons.mother_id==0]
                centers = np.array([primary_electrons_event.final_x.values, primary_electrons_event.final_y.values, primary_electrons_event.final_z.values]).T
                GetBlobDensity(event_hits, centers, mc['dir'])
