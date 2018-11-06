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
from geometry.airfoil import Airfoil


class Domain(object):

    def __init__(self, airfoil_in, upstream=13., top=13., bottom=13., wake=20.):
        """ Constructs the points defining the domain used to simulate the airfoil

        :param Airfoil airfoil_in: Input airfoil to construct the domain around
        :param float upstream: Normalized dimension in front of the leading edge of the airfoil
        :param float top: Normalized dimension above the airfoil
        :param float bottom: Normalized dimension below the airfoil
        :param float wake: Normalized dimension behind the trailing edge of the airfoil
        """

        self.airfoil_in = airfoil_in
        self.upstream, self.top, self.bottom, self.wake = upstream, top, bottom, wake

    def write_dat(self, filename=None, extension='_DOMAIN.dat'):
        """ Writes modified airfoil ordinates to .dat file """
        filename = filename if filename is not None else os.path.join(self.default_directory, self.__name__ + extension)
        top_pnts, bot_pnts = self.ordinates['top'], self.ordinates['bot']

        def point_format(open_file, point):
            return open_file.write('  {:1.6f}  {:1.6f}  {:1.6f}\n'.format(point.x, point.y, point.z).replace('-0', '-'))

        with open(filename, 'w') as output:
            output.write('# {} AIRFOIL MODDED AoA = {} deg\n'.format(self.__name__, self.angle))
            output.write(' {:d} 0\n'.format(len(top_pnts)))
            [point_format(output, pnt) for pnt in top_pnts]  # Writes top points in group to file w/ list comprehension

            output.write(' {:d} 0\n'.format(len(bot_pnts)))
            [point_format(output, pnt) for pnt in bot_pnts]



