from directories import DIRS
import os
from math import sqrt
from inflow import rho, mu

with open(os.path.join(DIRS['DATA_DIR'], 'shear', 'coarse_wallshear.csv')) as f:
    lines = f.readlines()[5:]
    lines = [[float(entry) for entry in line.replace(' ', '').replace('\n', '').split(',') if entry != '']
             for line in lines]
    average_shear = sum([i[1] for i in lines])/len(lines)

u_tau = sqrt(average_shear/rho)

h = mu / u_tau


def first_cell_height(y_plus=0.5):
    """ Computes Cell Height from a desired y+ value """
    return y_plus * mu / u_tau


print('First Cell Height <= {} for y+ <1'.format(first_cell_height(0.5)))
