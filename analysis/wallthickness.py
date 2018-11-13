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
from directories import DIRS
from utils import Attribute


class WallThickness(object):

    @Attribute
    def working_directory(self):
        """ Fetches the working directory of the current run_case """
        return os.path.join(DIRS['DATA_DIR'], 'yplus')

    @Attribute
    def required_plots(self):
        return ['yplus_fine_final', 'yplus_coarse_final']

    @Attribute
    def data_dict(self):
        _dict = {}
        for plot in self.required_plots:
            key = 'Fine SST' if 'fine' in plot else 'Coarse SST'
            _dict[key] = self.read_cfx(os.path.join(self.working_directory, '{}.csv'.format(plot)))
        return _dict

    def read_cfx(self, filename=None):
        """ Reads y-plus coefficient data from output CFX .dat file. Due to the definition of the polyline the data
        is unordered. Thus first a complete curve is constructed. Then the normalized x-values and pressure coefficients
        are retured in a dict

        :rtype: dict
        """
        with open(filename, 'r') as data:

            read_lines = data.readlines()[5:]
            float_tuples = [[float(num) for num in line.replace('\n', '').split(', ') if num != '']
                            for line in read_lines if line != '\n']

            # Fixing un-ordered data that starts somehwere on the upper-surface due to polyline
            min_idx = float_tuples.index(min(float_tuples, key=lambda x: x[0]))
            max_idx = float_tuples.index(max(float_tuples, key=lambda x: x[0]))
            min_x = float_tuples[min_idx][0]
            max_x = float_tuples[max_idx][0]

            top_rear_half = float_tuples[0:max_idx+1]
            top_front_half = float_tuples[min_idx:]
            top_surface = top_front_half + top_rear_half
            bottom_surface = float_tuples[max_idx:min_idx+1]

            print(top_surface)

            def normalize(e):
                return (e[0] - min_x) / (max_x - min_x)

        return {'x_top': [normalize(entry) for entry in top_surface],
                'y_top': [entry[1] for entry in top_surface],
                'x_bot': [normalize(entry) for entry in bottom_surface],
                'y_bot': [entry[1] for entry in bottom_surface]}

    def plot_fine(self, save=True):
        """ Plots fine mesh y-plus"""

        fig = plt.figure('WallThickness')
        plt.style.use('tudelft')

        # Plotting Refined Mesh Result (SST)
        y_plus = self.data_dict['Fine SST']
        x_top, y_top = y_plus['x_top'], y_plus['y_top']
        x_bot, y_bot = y_plus['x_bot'], y_plus['y_bot']
        plt.plot(x_top, y_top, label='Upper Surface', linewidth=1.)
        plt.plot(x_bot, y_bot, label='Lower Surface', linewidth=1.)

        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Dimensionless Wall Thickness, ($y^+$) [-]')
        plt.title(r'Fine SST Dimensionless Wall Thickness')
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], 'yplus_fine'))

    def plot_coarse(self, save=True):
        """ Plots coarse mesh y-plus"""

        fig = plt.figure('WallThickness')
        plt.style.use('tudelft')

        # Plotting Refined Mesh Result (SST)
        y_plus = self.data_dict['Coarse SST']
        x_top, y_top = y_plus['x_top'], y_plus['y_top']
        x_bot, y_bot = y_plus['x_bot'], y_plus['y_bot']
        plt.plot(x_top, y_top, label='Upper Surface', linewidth=1.)
        plt.plot(x_bot, y_bot, label='Lower Surface', linewidth=1.)

        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Dimensionless Wall Thickness, ($y^+$) [-]')
        # plt.title(r'Coarse SST Dimensionless Wall Thickness')
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], 'yplus_coarse'))


if __name__ == '__main__':
    obj = WallThickness()
    print(obj.data_dict)
    obj.plot_coarse()
    obj.plot_fine()
