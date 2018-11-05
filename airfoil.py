#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright [yyyy] [name of copyright owner]
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


class Airfoil(object):

    def __init__(self, airfoil_name='RAE2822'):
        self.__name__ = airfoil_name

    @property
    def default_directory(self):
        return os.path.abspath('data')

    def read_ord(self, filename=None, extension='.dat'):
        """ Reads airfoil ordinates from .dat file """
        filename = filename if filename is not None else os.path.join(self.default_directory, self.__name__ + extension)
        with open(filename, 'r') as data:
            split_lines = [line.replace('\n', '').split(' ') for line in data.readlines()[2:]]
            converted_lines = [[float(entry) for entry in line if entry != ''] for line in split_lines]
            filtered_lines = [(line[0], line[1]) for line in converted_lines if line != []]

            idx = filtered_lines.index((65.0, 0.0))
            surfaces = filtered_lines[0:idx], filtered_lines[idx+1:]

        return {'top': surfaces[0], 'bot': surfaces[1]}


if __name__ == '__main__':
    obj = Airfoil()
    lines = obj.read_ord()
    lines2 = obj.read_cp()
    obj.plot_cp()
    obj.plot_airfoil()
    print(obj.read_cp()['alpha'])
