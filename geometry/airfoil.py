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
from geometry.definitions import Point
from directories import DIRS
from matplotlib import pyplot as plt
import numpy as np
import scipy.interpolate as si
import scipy.optimize as so

# Reference:
# https://github.com/chiefenne/PyAero/blob/master/src/SplineRefine.py


class Airfoil(object):

    __cache__ = {'test': None}

    def __init__(self, airfoil_name='RAE2822', angle=0.):
        """

        :param str airfoil_name: Name of the airfoil w/o file extension
        :param float angle: Angle of Attack in SI degree [deg]
        """
        self.__name__, self.angle, self.ordinates = airfoil_name, angle, None

        # Updates ordinates from .dat file
        self.read_dat()

    @property
    def default_directory(self):
        return os.path.join(DIRS['DATA_DIR'], 'geom')

    def read_dat(self, filename=None, extension='.dat'):
        """ Reads airfoil ordinates from .dat file """
        filename = filename if filename is not None else os.path.join(self.default_directory, self.__name__ + extension)

        def str_to_point(str_list):
            """ List must be a str of format `  x  y  z` """
            # TODO make automatic detection of delimeter
            return [Point(*[float(entry) for entry in line.split('  ') if entry != '']) for line in str_list]

        with open(filename, 'r') as data:
            read_lines = [line.replace('\n', '') for line in data.readlines()]
            [read_lines.pop(i) for i, line in enumerate(read_lines) if '#' in line]  # Removing comments

            # Finding top & bottom curve groups
            group_indices = [i for i, line in enumerate(read_lines) if not line.startswith('  ')]
            top_lines = read_lines[group_indices[0]+1:group_indices[-1]]
            bottom_lines = read_lines[group_indices[-1]+1:]

            top_points, bottom_points = str_to_point(top_lines), str_to_point(bottom_lines)
            setattr(self, 'ordinates', {'top': top_points, 'bot': bottom_points})

    def write_dat(self, filename=None, extension='_mod.dat'):
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

    @property
    def spline(self):
        """ Interpolate spline through given points
        Args:
            spline (int, optional): Number of points on the spline
            degree (int, optional): Degree of the spline
            evaluate (bool, optional): If True, evaluate spline just at
                                       the coordinates of the knots
        """
        # interpolate B-spline through data points
        # returns knots of control polygon
        # tck ... tuple (t,c,k) containing the vector of knots,
        # the B-spline coefficients, and the degree of the spline.
        # u ... array of the parameters for each knot
        # NOTE: s=0.0 is important as no smoothing should be done on the spline
        # after interpolating it

        # ord_dict = self.get_ordinates()
        # top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
        #
        # top_spline, u, = si.splprep((top_x, bot_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc
        # bot_spline, u, = si.splprep((bot_x, bot_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc

        # # number of points on interpolated B-spline (parameter t)
        # t = np.linspace(0.0, 1.0, n)
        #
        # # if True, evaluate spline just at the coordinates of the knots
        #
        # # evaluate B-spline at given parameters
        # # der=0: returns point coordinates
        # coo = si.splev(t, spline_vector, der=0)
        #
        # # evaluate 1st derivative at given parameters
        # der1 = si.splev(t, spline_vector, der=1)
        #
        # # evaluate 2nd derivative at given parameters
        # der2 = si.splev(t, spline_vector, der=2)
        #
        # # spline_data = [coo, u, t, der1, der2, spline_vector]
        #
        # return top_spline, bot_spline

    @spline.getter
    def spline(self):
        if 'spline' in self.__cache__.keys():
            return self.__cache__['spline']
        else:
            ord_dict = self.get_ordinates()
            top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])

            top_spline, u, = si.splprep((top_x, top_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc
            bot_spline, u, = si.splprep((bot_x, bot_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc
            self.__cache__['spline'] = top_spline, bot_spline
            return top_spline, bot_spline

    def make_spline(self):
        top, bot = self.read_dat()
        top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
        bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
        top_x = list(reversed(top_x))[:-1]
        top_y = list(reversed(top_y))[:-1]

        x = top_x + bot_x
        y = top_y + bot_y

        spline_data = self.spline(x, y)

        curvature = self.getCurvature(spline_data)

        plt.plot(spline_data[0][0], spline_data[0][1])
        plt.plot(curvature[3], curvature[4])
        plt.axis([0, 1, -0.5, 0.5])
        plt.show()
        return spline_data

    @staticmethod
    def getCurvature(spline_data):
        """Curvature and radius of curvature of a parametric curve
        der1 is dx/dt and dy/dt at each point
        der2 is d2x/dt2 and d2y/dt2 at each point

        Returns:
            list: Tuple of numpy arrays carrying gradient of the curve,
                   the curvature, radiusses of curvature circles and
                   curvature circle centers for each point of the curve
        """

        coo = spline_data[0]
        der1 = spline_data[3]
        der2 = spline_data[4]

        xd = der1[0]
        yd = der1[1]
        x2d = der2[0]
        y2d = der2[1]
        n = xd ** 2 + yd ** 2
        d = xd * y2d - yd * x2d

        # gradient dy/dx = dy/du / dx/du
        gradient = der1[1] / der1[0]

        # radius of curvature
        R = n ** (3. / 2.) / abs(d)

        # curvature
        C = d / n ** (3. / 2.)

        # coordinates of curvature-circle center points
        xc = coo[0] - R * yd / np.sqrt(n)
        yc = coo[1] + R * xd / np.sqrt(n)

        return [gradient, C, R, xc, yc]

    def get_maxima(self):

        top, bot = self.spline

        def objective(u, *args):
            spline = args[0]
            slope = si.splev(u, spline, der=1)
            return (slope[1] / slope[0])**2  # slope dy/dx = dy/du / dx/du

        u_top = so.fminbound(objective, 0., 1., args=(top,))
        u_bot = so.fminbound(objective, 0., 1., args=(bot,))

        top_max, bot_max = si.splev(u_top, top, der=0), si.splev(u_bot, bot, der=0)
        return top_max, bot_max

    def plot(self):
        """ Plots the Airfoil Geometry """
        top, bot = self.ordinates['top'], self.ordinates['bot']
        top, bot = [pnt.rotate(-self.angle) for pnt in top], [pnt.rotate(-self.angle) for pnt in bot]
        top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
        bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
        plt.plot(top_x, top_y)
        plt.plot(bot_x, bot_y)
        plt.axis([0, 1, -0.5, 0.5])
        plt.show()
        return None

    def get_ordinates(self):
        """ Retrieves the top and bottom coordinates of the

        :rtype: dict
        """
        top, bot = self.ordinates['top'], self.ordinates['bot']
        top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
        bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
        return {'top': (top_x, top_y), 'bot': (bot_x, bot_y)}


    # def read_cp(self, filename=None, extension='_cp.dat'):
    #     """ Reads airfoil ordinates from .dat file """
    #     filename = filename if filename is not None else os.path.join(self.default_directory, self.__name__ + extension)
    #     with open(filename, 'r') as data:
    #         read_lines = data.readlines()
    #         header = read_lines[0:3]
    #         split_lines = [line.replace('\n', '').split(' ', 1) for line in read_lines[3:]]
    #         space_removed_lines = [[entry.replace(' ', '') for entry in line] for line in split_lines]
    #         float_lines = [[float(entry) for entry in line if entry != ''] for line in space_removed_lines]
    #
    #         idx = float_lines.index([])
    #         top_surface = float_lines[0:idx]
    #         bottom_surface = float_lines[idx+1:-1]
    #
    #     return top_surface, bottom_surface
    #
    # def plot_cp(self):
    #     cp = self.read_cp()
    #     top_x = [line[0] for line in cp]
    #     top_cp = [line[1] for line in cp]
    #     plt.plot(top_x, top_cp)
    #     plt.show()
    #     return None


if __name__ == '__main__':
    obj = Airfoil(angle=2.31)
    obj.plot()
    obj.write_dat()
    print(obj.get_maxima())
    # lines2 = obj.read_cp()
    # obj.plot_cp()
    # print(lines2)
