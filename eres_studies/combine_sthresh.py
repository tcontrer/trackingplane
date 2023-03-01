import glob

data = {'s1.3mmp2.4mm':{'Eres':[], 'Eu':[], 'sthresh':[]}, 
        's1.3mmp3.5mm':{'Eres':[], 'Eu':[], 'sthresh':[]}, 
        's3mmp5.5mm':{'Eres':[], 'Eu':[], 'sthresh':[]}}
print(data.keys())
data_dir = 'data_eres_kr83m_rcut300.0_zcut1200.0'
event_type = 'kr83m'
files = glob.glob(data_dir+'/*.out')
files = sorted(files)
for out_file in files:
    sthresh = out_file.split('/')[1].split('_')[2].split('sthresh')[-1]
    config = out_file.split('/')[1].split('_')[1]
    print(config)
    data[config]['sthresh'].append(int(sthresh))
    with open(out_file) as f:
        lines = f.readlines()
        for line in lines:
            if 'Eres' in line:
                this = line.split('=')
                if 'Eres(FWHM)     (%)' in this[0]:
                    data[config]['Eres'].append(float(line.split('=')[-1]))
            if 'Eres err' in line:
                data[config]['Eu'].append(float(line.split()[-1]))

print(data)
#json.dump(data, open(data_dir+'all_data.txt', 'w'))
