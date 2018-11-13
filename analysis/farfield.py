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
from analysis.inflow import V


class FarfieldPlot(object):

    def __init__(self, run_case='fine_mesh_SST', title='Convergence History'):
        self.run_case = run_case
        self.title = title

    @Attribute
    def required_plots(self):
        return ['heat', 'inlet', 'momentum', 'turbulence']

    @Attribute
    def working_directory(self):
        """ Fetches the working directory of the current run_case """
        return os.path.join(DIRS['DATA_DIR'], 'farfield')

    @Attribute
    def data_dict(self):
        _dict = {}
        for csv_file in os.listdir(self.working_directory):
            with open(os.path.join(self.working_directory, csv_file)) as f:
                data = [line.replace('\n', '') for line in f.readlines() if line != '\n']
                header_idx = data.index('[Data]') + 1

                data = data[header_idx:]
                header = data.pop(0).split(',')
                labels = [l.replace('"', '') for l in header]
                #
                # Converting string lines to
                data = [[float(num) for num in line.split(',')] for line in data if line != []]

                # Type of Run
                run = 'SST' if 'SST' in csv_file else 'SSG'
                # Assigning current data-set to dictionary
                _dict[run] = {'data': data, 'labels': labels}
        return _dict

    def plot(self, save=True):
        """ Plots the difference in pressure coefficients between experimental data due to numerical diffusion """

        fig = plt.figure('Farfield')
        plt.style.use('tudelft')

        # Plotting Refined Mesh Result (SST)
        x, y = self.fetch_column('SST', 0), self.fetch_column('SST', 1)
        plt.plot(x, y, label='Fine SST', linewidth=1.)

        # Plotting Refined Mesh Result (SSG)
        x, y = self.fetch_column('SSG', 0), self.fetch_column('SSG', 1)
        plt.plot(x, y, label='Fine SSG', linewidth=1., linestyle='--')

        # plt.axis([-0, 1.0, 1.5, -1.5])
        plt.legend()
        plt.xlabel(r'Farfield Velocity $\left[\mathrm{m/s}\right]$')
        plt.ylabel(r'Y-Location on Domain Outlet $\left[\mathrm{m}\right]$')
        # plt.title(r'Farfield Velocity Profile $\left(U_{\infty} = %.2f\ \left[\mathrm{m/s}\right]\right)$' %V)
        plt.annotate(r'$\mathrm{M}=0.729,\ \mathrm{Re}=6\cdot 10^6,\ '
                     r' \alpha=2.31^{\circ}$', xy=(1, 0),
                     xycoords='axes fraction', horizontalalignment='right',
                     verticalalignment='bottom', fontsize='small')
        plt.show()
        if save:
            fig.savefig(os.path.join(DIRS['FIGURE_DIR'], 'farfield'))

    # def plot(self, show=False):
    #     def subplot_style(axis, xlabel='', ylabel='', legend=True, sci=False):
    #         axis.yaxis.set_tick_params(labelsize=7, pad=1)
    #         axis.xaxis.set_tick_params(labelsize=7)
    #         axis.set_xlabel(xlabel)
    #         axis.set_ylabel(ylabel, labelpad=0)
    #         if legend:
    #             axis.legend(loc='best', fontsize=7)
    #         if sci:
    #             axis.ticklabel_format(style='sci', scilimits=(-3, 4), axis='y')
    #         # axis.grid(b=True, which='both', linestyle='-')
    #
    #     # fig = plt.figure('%s_convergence' % self.run_case, figsize=(7.2, 7.2))
    #     plt.style.use('tudelft')
    #     fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1, num='{}_convergence'.format(self.run_case), sharex='all',
    #                                              gridspec_kw={'top': 0.95, 'hspace': 0.15}, figsize=(7.2, 7.2))
    #     fig.set_tight_layout(False)
    #
    #     # Localizing Variables for clarity
    #     d, f = self.data_dict, self.fetch_column
    #
    #     # Plotting Momentum Residual
    #     for i, str_label in enumerate(d['momentum']['labels']):
    #         try:
    #             if i != 0:
    #                 ax0.plot(f('momentum', 0), f('momentum', i), label=str_label, linewidth=1.0)
    #         except Exception as e:
    #             raise e
    #     ax0.set_yscale("log", nonposy='clip')
    #     subplot_style(ax0, '', r'Mass & Momentum')
    #
    #     # Plotting Turbulence Residual
    #     for i, str_label in enumerate(d['turbulence']['labels']):
    #         try:
    #             if i != 0:
    #                 ax1.plot(f('turbulence', 0), f('turbulence', i), label=str_label, linewidth=1.0)
    #         except Exception as e:
    #             raise e
    #     ax1.set_yscale("log", nonposy='clip')
    #     subplot_style(ax1, '', r'Turbulence')
    #
    #     # Plotting Turbulence Residual
    #     ax2.plot(f('heat', 0), f('heat', 1), linewidth=1.0, label='RMS H-Energy')
    #     ax2.set_yscale("log", nonposy='clip')
    #     subplot_style(ax2, '', r'Heat Trans.')
    #
    #     # Plotting U-Momentum
    #     ax3.plot(f('inlet', 0), f('inlet', 1), linewidth=1.0, label='U-Mom')
    #     subplot_style(ax3, 'Accumulated Time Step', r'Inlet Momentum', sci=True)
    #
    #     fig.suptitle(self.title, fontsize=10)
    #     # plt.tight_layout()
    #     if show:
    #         plt.show()
    #     fig.savefig(fname=os.path.join(DIRS['FIGURE_DIR'], '%s' % fig.get_label()))

    def fetch_column(self, key, col):
        try:
            return [x[col] for x in self.data_dict[key]['data']]
        except IndexError as e:
            raise e


if __name__ == '__main__':
    obj = FarfieldPlot()
    print(os.listdir(obj.working_directory))
    print(obj.data_dict.keys())
    obj.plot()

    # obj = ConvergencePlot('fine_mesh_SST', 'Fine Mesh SST Convergence History')
    # obj.plot()
    # obj = ConvergencePlot('fine_mesh_SSG', 'Fine Mesh SSG Convergence History')
    # obj.plot()
    # obj = ConvergencePlot('coarse_mesh_SST', 'Coarse Mesh SST Convergence History')
    # obj.plot()
    # obj = ConvergencePlot('coarse_mesh_upwind', 'Coarse Mesh Upwind Convergence History')
    # obj.plot()
    # obj = ConvergencePlot('Fine_mesh_upwind', 'Fine Mesh Upwind Convergence History')
    # obj.plot()
