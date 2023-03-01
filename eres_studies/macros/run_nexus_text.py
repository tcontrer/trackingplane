import os
import json

mcs = {'s1.3mmp3.5mm':
        {'size':1.3, 'pitch':3.5,  'teflon':False, 'nsipms':61053,   'run':True},
    's1.3mmp2.4mm':
        {'size':1.3, 'pitch':2.4,    'teflon':False, 'nsipms':129889,  'run':True},
    's3mmp5.5mm':
        {'size':3, 'pitch':5.5,  'teflon':False, 'nsipms':24748, 'run':True}}

# RunEres 
event_type = '0vbb'
nfiles = 1000 # 100 total for kr83m, 1000 total for 0vbb
rcut = 300. # mm
zcut = 1200. # mm
base_sipm_thresh = 2 # pes
outdir = f'/n/home12/tcontreras/plots/FlexEresStudies/{event_type}/'
partition = 'serial_requeue'

def RunBatchEres(event_type, nfiles, rcut, zcut, base_sipm_thresh, outdir, mcs):

    jobfile_name = 'jobids_eres_'+event_type+'.txt'
    with open(jobfile_name, 'w') as jf:

        jf.write(f'Job IDs for Distributions of {event_type} Simulations:\n')
        for name in mcs:
            mc = mcs[name]
            if mc['run']:
                jf.write(name+'\n')
                batchfile_name = 'run_nexus_'+event_type+'_'+name+'.sh'
                inputs = f"{name} {event_type} {outdir}"

                with open('macros/'+batchfile_name, 'w') as f:
                    f.write("#!/bin/bash\n")
                    f.write("#SBATCH -n 1                                   # Number of cores\n")
                    f.write("#SBATCH -N 1                                   # Ensure that all cores are on one machine\n")           
                    f.write("#SBATCH -t 0-1:00                              # Runtime in D-HH:MM, minimum of 10 minutes\n")
                    f.write(f"#SBATCH -p {partition}                          # Partition to submit to\n")
                    f.write("#SBATCH --mem=5000                             # Memory pool for all cores (see also --mem-per-cpu)\n")
                    f.write(f"#SBATCH -o out/nexus_{event_type}_{name}.out  # File to which STDOUT will be written, %j inserts jobid\n")
                    f.write(f"#SBATCH -e err/nexus_{event_type}_{name}.err  # File to which STDERR will be written, %j inserts jobid\n")                 
                    f.write("\n")
                    f.write("source /n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/eres_22072022/IC_setup.sh\n")
                    f.write("\n")
                    f.write(f"python  /n/holystore01/LABS/guenette_lab/Lab/data/NEXT/FLEX/mc/eres_22072022/eres_taylor/macros/test_nexus.py {inputs}\n")

                os.system(f"sbatch macros/{batchfile_name} > out/temp.txt")
                with open('out/temp.txt', 'r') as f:
                    jf.write(f.readlines()[0])


if __name__ == '__main__':

    RunBatchEres(event_type, nfiles, rcut, zcut, base_sipm_thresh, outdir, mcs)