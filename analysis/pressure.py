#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 San Kilkis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import matplotlib.pyplot as plt
from geometry.airfoil import Airfoil
from directories import DIRS


class PressureCoefficient(object):

    def __init__(self, airfoil_in=Airfoil()):
        self.airfoil_in = airfoil_in

    def read_cp(self, filename=None, extension='_cp.dat'):
        """ Reads airfoil ordinates from .dat file """
        filename = filename if filename is not None else os.path.join(DIRS['DATA_DIR'], 'pressure',
                                                                      self.airfoil_in.__name__ + extension)
        with open(filename, 'r') as data:
            read_lines = data.readlines()
            header = [line for line in read_lines if line.startswith('#')]
            split_lines = [line.replace('\n', '').split(' ', 1) for line in read_lines if line not in header]
            space_removed_lines = [[entry.replace(' ', '') for entry in line] for line in split_lines]
            float_lines = [[float(entry) for entry in line if entry != ''] for line in space_removed_lines]

            idx = float_lines.index([])
            surfaces = (float_lines[0:idx], float_lines[idx+1:-1])
            sorted_surfaces = sorted(surfaces, key=lambda x: min(x))
            top_surface, bottom_surface = sorted_surfaces[1], sorted_surfaces[0]

            # Obtaining Values from Header
            filtered_header = [line.replace('\n', '').replace('# ', '') for line in header]
            states = filtered_header[1].split(',')

            def fetch_state(state):
                key, value = state.split('=', 1)

                # Obtaining Key
                key = key.replace(' ', '')

                # Obtaining Value
                value_list = value.split(' ')
                # if len(value_list) != 2:
                #     raise ValueError('Provided state does not have the proper format key = value unit')

                value = 0
                for val in value_list:
                    try:
                        float(val)
                        value = val
                    except Exception as e:
                        pass

                return key, value

            mach, alpha = fetch_state(states[0]), fetch_state(states[1])

        return {'top': top_surface, 'bot': bottom_surface, 'alpha': alpha, 'mach': mach}

    def read_cfx(self, filename=None, extension='_cp.dat'):
        """ Reads pressure coefficient data from output CFX .dat file. Due to the definition of the polyline the data
        is unordered. Thus first a complete curve is constructed. Then the normalized x-values and pressure coefficients
        are retured in a dict

        :rtype: dict
        """
        filename = filename if filename is not None else os.path.join(DIRS['DATA_DIR'], 'pressure',
                                                                      self.airfoil_in.__name__ + extension)

        with open(filename, 'r') as data:

            read_lines = data.readlines()[5:]
            float_tuples = [[float(num) for num in line.replace('\n', '').split(', ') if num != '']
                            for line in read_lines if line != '\n']

            # Fixing un-ordered data that starts somehwere on the upper-surface due to polyline
            min_idx = float_tuples.index(min(float_tuples, key=lambda x: x[0]))
            max_idx = float_tuples.index(max(float_tuples, key=lambda x: x[0]))
            min_x = float_tuples[min_idx][0]
            max_x = float_tuples[max_idx][0]

            top_rear_half = float_tuples[0:min_idx+1]
            top_front_half = float_tuples[max_idx:]
            top_surface = top_front_half + top_rear_half
            bottom_surface = float_tuples[min_idx:max_idx+1]
            complete_curve = top_surface + bottom_surface

        return {'x': [((entry[0] - min_x) / (max_x - min_x)) for entry in complete_curve],
                'y': [entry[1] for entry in complete_curve]}

    def plot_turbulence(self, save=True):
        """ Plots the difference in pressure coefficients between experimental data, a coarse and fine mesh with SST
        turbulence model, as well as a fine mesh with a SSG turbulence model. This is to depict the differences between
        turbulence models. """

        fig = plt.figure('{}PressureDistribution'.format(self.airfoil_in.__name__))
        plt.style.use('tudelft')

        # Plotting Refined Mesh Result (SST)
        cp_crs = self.read_cfx(extension='_cp_fine_SST.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Fine SST', linewidth=1.)

        # Plotting Refined Mesh Result (SSG)
        cp_crs = self.read_cfx(extension='_cp_fine_SSG_converged.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Fine SSG', linestyle='--', linewidth=1.)

        # Plotting experimental data froM NASA
        cp_wt = self.read_cp(extension='_cp_test.dat')
        top_x, top_cp = [line[0] for line in cp_wt['top']], [line[1] * -1. for line in cp_wt['top']]
        bot_x, bot_cp = [line[0] for line in cp_wt['bot']], [line[1] * -1. for line in cp_wt['bot']]
        plt.scatter(top_x, top_cp, label='Experiment, Top Surface', marker='o', s=10., facecolor='w',
                    edgecolors='k', zorder=3)
        plt.scatter(bot_x, bot_cp, label='Experiment, Bottom Surface', marker='s', s=10., facecolor='w',
                    edgecolors='k', zorder=3)

        plt.axis([-0, 1.0, 1.5, -1.5])
        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Pressure Coefficient [-]')
        # plt.title(r'%s Pressure Distribution' % self.airfoil_in.__name__)
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], '{}_cp_turbulence'.format(self.airfoil_in.__name__)))

    def plot_diffusion(self, save=True):
        """ Plots the difference in pressure coefficients between experimental data due to numerical diffusion """

        fig = plt.figure('{}PressureDistribution'.format(self.airfoil_in.__name__))
        plt.style.use('tudelft')

        # Plotting Refined Mesh Result (SST)
        cp_crs = self.read_cfx(extension='_cp_fine_upwind.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Fine Upwind', linewidth=1.)

        # Plotting Refined Mesh Result (SSG)
        cp_crs = self.read_cfx(extension='_cp_coarse_upwind.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Coarse Upwind', linestyle='--', linewidth=1.)

        # Plotting experimental data froM NASA
        cp_wt = self.read_cp(extension='_cp_test.dat')
        top_x, top_cp = [line[0] for line in cp_wt['top']], [line[1] * -1. for line in cp_wt['top']]
        bot_x, bot_cp = [line[0] for line in cp_wt['bot']], [line[1] * -1. for line in cp_wt['bot']]
        plt.scatter(top_x, top_cp, label='Experiment, Top Surface', marker='o', s=10., facecolor='w',
                    edgecolors='k', zorder=3)
        plt.scatter(bot_x, bot_cp, label='Experiment, Bottom Surface', marker='s', s=10., facecolor='w',
                    edgecolors='k', zorder=3)

        plt.axis([-0, 1.0, 1.5, -1.5])
        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Pressure Coefficient [-]')
        # plt.title(r'%s Pressure Distribution' % self.airfoil_in.__name__)
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], '{}_cp_diffusion'.format(self.airfoil_in.__name__)))

    def plot_mesh(self, save=True):
        """ Plots the difference in pressure coefficients between experimental data, a coarse and fine mesh with SST
        turbulence model, as well as a fine mesh with a SSG turbulence model. This is to depict the differences between
        turbulence models. """

        fig = plt.figure('{}PressureDistribution'.format(self.airfoil_in.__name__))
        plt.style.use('tudelft')

        # Plotting Coarse Mesh Result
        cp_crs = self.read_cfx(extension='_cp_coarse_SST.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Coarse SST', linestyle='-.', linewidth=1.)

        # Plotting Refined Mesh Result (SST)
        cp_crs = self.read_cfx(extension='_cp_fine_SST.dat')
        x, y = cp_crs['x'], cp_crs['y']
        plt.plot(x, y, label='Fine SST', linewidth=1.)

        # Plotting experimental data froM NASA
        cp_wt = self.read_cp(extension='_cp_test.dat')
        top_x, top_cp = [line[0] for line in cp_wt['top']], [line[1] * -1. for line in cp_wt['top']]
        bot_x, bot_cp = [line[0] for line in cp_wt['bot']], [line[1] * -1. for line in cp_wt['bot']]
        plt.scatter(top_x, top_cp, label='Experiment, Top Surface', marker='o', s=10., facecolor='w',
                    edgecolors='k', zorder=3)
        plt.scatter(bot_x, bot_cp, label='Experiment, Bottom Surface', marker='s', s=10., facecolor='w',
                    edgecolors='k', zorder=3)

        plt.axis([-0, 1.0, 1.5, -1.5])
        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Pressure Coefficient [-]')
        # plt.title(r'%s Pressure Distribution' % self.airfoil_in.__name__)
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], '{}_cp_mesh'.format(self.airfoil_in.__name__)))

    def add_data(self):
        return None


if __name__ == '__main__':
    obj = PressureCoefficient()
    obj.plot_turbulence()
    obj.plot_diffusion()
    obj.plot_mesh()
