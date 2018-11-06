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
from geometry.definitions import Point
from directories import DIRS


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

    @property
    def default_directory(self):
        return os.path.join(DIRS['DATA_DIR'], 'geom')

    def write_dat(self, filename=None, extension='_DOMAIN.dat'):
        """ Writes modified airfoil ordinates to .dat file """
        name = self.airfoil_in.__name__
        filename = filename if filename is not None else os.path.join(self.default_directory, name + extension)

        def point_format(open_file, point):
            return open_file.write('  {:1.6f}  {:1.6f}  {:1.6f}\n'.format(point.x, point.y, point.z).replace('-0', '-'))

        # Gathering Coordinates
        x_center = self.airfoil_in.center.x
        x_le = self.airfoil_in.leading_edge.x
        x_te = self.airfoil_in.trailing_edge.x

        pt_1 = Point(x_center, self.top, 0)
        pt_2 = Point(x_te + self.wake, self.top, 0)
        pt_3 = Point(pt_2.x, -self.bottom, 0)
        pt_4 = Point(x_center, -self.bottom, 0)
        pt_5 = Point(x_le - self.upstream, 0, 0)

        with open(filename, 'w') as output:
            output.write('# {} AIRFOIL DOMAIN\n'.format(name))

            # Segment 1-2
            output.write(' {:d} 0\n'.format(2))
            point_format(output, pt_1)
            point_format(output, pt_2)

            # Segment 2-3
            output.write(' {:d} 0\n'.format(2))
            point_format(output, pt_2)
            point_format(output, pt_3)

            # Segment 3-4
            output.write(' {:d} 0\n'.format(2))
            point_format(output, pt_3)
            point_format(output, pt_4)

            # Segment 4-1
            output.write(' {:d} 0\n'.format(3))
            point_format(output, pt_4)
            point_format(output, pt_5)
            point_format(output, pt_1)


if __name__ == '__main__':
    domain = Domain(airfoil_in=Airfoil(angle=2.31))
    domain.write_dat()




