#!/bin/bash
#SBATCH -n 1                # Number of cores
#SBATCH -N 1                # Ensure that all cores are on one machine
#SBATCH -t 1-0:00          # Runtime in D-HH:MM, minimum of 10 minutes
#SBATCH -p guenette   # Partition to submit to
#SBATCH --mem=100000          # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o jobinfo/myoutput_cuts_kr.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e jobinfo/myerrors_cuts_kr.err  # File to which STDERR will be written, %j inserts jobid

source /n/holystore01/LABS/guenette_lab/Users/tcontreras/IC_setup2020.sh

python  /n/holystore01/LABS/guenette_lab/Users/tcontreras/trackingplane/sipmstudy_cuts.py
