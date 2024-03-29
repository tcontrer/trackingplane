import json

#configs = ['s1.3mmp15mm', 's1.3mmp7mm', 's1.3mmp1.3mm', 
#            's3mmp15mm', 's3mmp7mm', 's3mmp3mm',
#            's6mmp15mm', 's6mmp6mm',
#           's1.3mmp15mm_teflon', 's1.3mmp7mm_teflon',
#            's3mmp15mm_teflon', 's3mmp7mm_teflon',
#            's6mmp15mm_teflon']

configs = ['s1.3mmp15mm', 's1.3mmp7mm', 's1.3mmp1.3mm',
           's1.3mmp5.82mm', 's1.3mmp4.11mm', 's1.3mmp2.9mm',
           's1.3mmp2.37mm', 's1.3mmp1.84mm',
           's3mmp15mm', 's3mmp7mm', 's3mmp3mm',
           's3mmp9.49mm', 's3mmp6.71mm', 's3mmp5.48mm',
           's3mmp4.74mm', 's3mmp4.24mm',
           's6mmp15mm', 's6mmp6mm',
           's6mmp18.97mm', 's6mmp13.42mm', 's6mmp10.95mm',
           's6mmp9.49mm', 's6mmp8.49mm'] 

data_dir = 'data_eres_kr83m_rcut300_sthresh2_zcut1200/'
data = {}
for config in configs:
    print(config)
    d = json.load(open(data_dir+config+'.txt'))
    data[config] = d
print(data)
json.dump(data, open(data_dir+'all_data.txt', 'w'))
