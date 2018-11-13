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


class ConvergencePlot(object):

    def __init__(self, run_case='fine_mesh_SST', title='Convergence History'):
        self.run_case = run_case
        self.title = title

    @Attribute
    def required_plots(self):
        return ['heat', 'inlet', 'momentum', 'turbulence']

    @Attribute
    def working_directory(self):
        """ Fetches the working directory of the current run_case """
        required_files = {u'{}.csv'.format(field) for field in self.required_plots}
        try:
            filepath = os.path.join(DIRS['DATA_DIR'], 'convergence', self.run_case)
            files = os.listdir(filepath)
            if required_files.issuperset(files):
                return filepath
        except Exception as e:
            raise e

    @Attribute
    def data_dict(self):
        _dict = {}
        for plot in self.required_plots:
            with open(os.path.join(self.working_directory, '{}.csv'.format(plot))) as file:
                data = [line.replace('\n', '') for line in file.readlines() if line != '\n']
                header_idx = data.index('[Data]') + 1

                data = data[header_idx:]
                header = data.pop(0).split(',')
                labels = [l.replace('"', '') for l in header]
                #
                # Converting string lines to
                data = [[float(num) if i > 0 else int(num) for i, num in enumerate(line.split(','))]
                        for line in data if line != []]

                # Assigning current data-set to dictionary
                _dict[plot] = {'data': data, 'labels': labels}
        return _dict

    def plot(self, show=False):
        def subplot_style(axis, xlabel='', ylabel='', legend=True, sci=False):
            axis.yaxis.set_tick_params(labelsize=7, pad=1)
            axis.xaxis.set_tick_params(labelsize=7)
            axis.set_xlabel(xlabel)
            axis.set_ylabel(ylabel, labelpad=0)
            if legend:
                axis.legend(loc='best', fontsize=7)
            if sci:
                axis.ticklabel_format(style='sci', scilimits=(-3, 4), axis='y')
            # axis.grid(b=True, which='both', linestyle='-')

        # fig = plt.figure('%s_convergence' % self.run_case, figsize=(7.2, 7.2))
        plt.style.use('tudelft')
        fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1, num='{}_convergence'.format(self.run_case), sharex='all',
                                                 gridspec_kw={'top': 0.95, 'hspace': 0.15}, figsize=(7.2, 7.2))
        fig.set_tight_layout(False)

        # Localizing Variables for clarity
        d, f = self.data_dict, self.fetch_column

        # Plotting Momentum Residual
        for i, str_label in enumerate(d['momentum']['labels']):
            try:
                if i != 0:
                    ax0.plot(f('momentum', 0), f('momentum', i), label=str_label, linewidth=1.0)
            except Exception as e:
                raise e
        ax0.set_yscale("log", nonposy='clip')
        subplot_style(ax0, '', r'Mass & Momentum')

        # Plotting Turbulence Residual
        for i, str_label in enumerate(d['turbulence']['labels']):
            try:
                if i != 0:
                    ax1.plot(f('turbulence', 0), f('turbulence', i), label=str_label, linewidth=1.0)
            except Exception as e:
                raise e
        ax1.set_yscale("log", nonposy='clip')
        subplot_style(ax1, '', r'Turbulence')

        # Plotting Turbulence Residual
        ax2.plot(f('heat', 0), f('heat', 1), linewidth=1.0, label='RMS H-Energy')
        ax2.set_yscale("log", nonposy='clip')
        subplot_style(ax2, '', r'Heat Trans.')

        # Plotting U-Momentum
        ax3.plot(f('inlet', 0), f('inlet', 1), linewidth=1.0, label='U-Mom')
        subplot_style(ax3, 'Accumulated Time Step', r'Inlet Momentum', sci=True)

        # fig.suptitle(self.title, fontsize=10)
        # plt.tight_layout()
        if show:
            plt.show()
        fig.savefig(fname=os.path.join(DIRS['FIGURE_DIR'], '%s' % fig.get_label()))

    def fetch_column(self, key, col):
        _d, idx = self.data_dict, self.required_plots.index(key)
        try:
            return [x[col] for x in _d[key]['data']]
        except IndexError as e:
            raise e


if __name__ == '__main__':
    obj = ConvergencePlot('fine_mesh_SST', 'Fine Mesh SST Convergence History')
    obj.plot()
    obj = ConvergencePlot('fine_mesh_SSG', 'Fine Mesh SSG Convergence History')
    obj.plot()
    obj = ConvergencePlot('coarse_mesh_SST', 'Coarse Mesh SST Convergence History')
    obj.plot()
    obj = ConvergencePlot('coarse_mesh_upwind', 'Coarse Mesh Upwind Convergence History')
    obj.plot()
    obj = ConvergencePlot('fine_mesh_upwind', 'Fine Mesh Upwind Convergence History')
    obj.plot()
