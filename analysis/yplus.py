from directories import DIRS
import os
from math import sqrt

with open(os.path.join(DIRS['DATA_DIR'], 'shear', 'coarse_wallshear.csv')) as f:
    lines = f.readlines()[5:]
    lines = [[float(entry) for entry in line.replace(' ', '').replace('\n', '').split(',') if entry != '']
             for line in lines]
    average_shear = sum([i[1] for i in lines])/len(lines)



from inflow import rho, mu
u_tau = sqrt(average_shear/rho)

h = mu / u_tau
print('First Cell Height <= {} for y+ <1'.format(h))
