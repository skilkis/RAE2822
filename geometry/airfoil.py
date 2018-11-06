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
from geometry.definitions import Point, Curve
from directories import DIRS
from matplotlib import pyplot as plt
import numpy as np
# import scipy.interpolate as si
import scipy.optimize as so

# Reference:
# https://github.com/chiefenne/PyAero/blob/master/src/SplineRefine.py


class Airfoil(object):

    def __init__(self, airfoil_name='RAE2822', angle=0.):
        """

        :param str airfoil_name: Name of the airfoil w/o file extension
        :param float angle: Angle of Attack in SI degree [deg]
        """
        self.__cache__ = {}
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

            # Applying rotation to points to achieve AoA
            top_points = [pnt.rotate(-self.angle) for pnt in top_points]
            bottom_points = [pnt.rotate(-self.angle) for pnt in bottom_points]

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
    def leading_edge(self):
        """ Fetches the leading-edge point from the ordinates

        :rtype: Point
        """
        return self.ordinates['top'][0]

    @property
    def trailing_edge(self):
        """ Fetches the trailing-edge point from the ordinates

        :rtype: Point
        """
        return self.ordinates['top'][-1]

    # @property
    # def spline(self):
    #     """ Interpolate spline through given points
    #     Args:
    #         spline (int, optional): Number of points on the spline
    #         degree (int, optional): Degree of the spline
    #         evaluate (bool, optional): If True, evaluate spline just at
    #                                    the coordinates of the knots
    #     """
    #     pass
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
    #
    # @spline.getter
    # def spline(self):
    #     if 'spline' in self.__cache__.keys():
    #         return self.__cache__['spline']
    #     else:
    #         ord_dict = self.get_ordinates()
    #         top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
    #
    #         top_spline, u, = si.splprep((top_x, top_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc
    #         bot_spline, u, = si.splprep((bot_x, bot_y), s=0.0, k=3)  # Ignore unpacking warning, it is due to Numpy doc
    #         self.__cache__['spline'] = top_spline, bot_spline
    #         return top_spline, bot_spline

    @property
    def curve(self):
        pass

    @curve.getter
    def curve(self):
        """ Returns a dictionary of airfoil curves. ['top'] = Top curve f/ LE -> TE, ['bot] = Bottom curve f/ LE -> TE
        ['complete'] = Complete airfoil curve from TE -> Top-Curve -> LE -> Bottom-Curve -> TE

        :rtype: dict
        """
        if 'curve' in self.__cache__.keys():
            return self.__cache__['curve']
        else:
            top_curve, bot_curve = Curve(self.ordinates['top']), Curve(self.ordinates['bot'])
            top_pnts_reversed = list(reversed(self.ordinates['top']))[:-1]
            complete_curve = Curve(top_pnts_reversed + self.ordinates['bot'])
            self.__cache__['curve'] = {'top': top_curve, 'bot': bot_curve, 'complete': complete_curve}
            return self.__cache__['curve']

    # def make_spline(self):
    #     top, bot = self.read_dat()
    #     top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
    #     bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
    #     top_x = list(reversed(top_x))[:-1]
    #     top_y = list(reversed(top_y))[:-1]
    #
    #     x = top_x + bot_x
    #     y = top_y + bot_y
    #
    #     spline_data = self.spline(x, y)
    #
    #     curvature = self.getCurvature(spline_data)
    #
    #     plt.plot(spline_data[0][0], spline_data[0][1])
    #     plt.plot(curvature[3], curvature[4])
    #     plt.axis([0, 1, -0.5, 0.5])
    #     plt.show()
    #     return spline_data

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
        """ Returns the parameter ``u`` on the top and bottom curves where the local tangent vector is parallel with the
        x-axis

        :return [0] Top curve ``u``, [1] Bottom curve ``u``
        :rtype: tuple[float]
        """

        top, bot = self.curve['top'], self.curve['bot']

        def objective(u, *args):
            curve = args[0]
            tan = curve.tangent(u)
            slope = tan.y/tan.x  # slope dy/dx = Vector.y/Vector.x
            return slope**2  # Finding where slope = zero

        u_top = so.fminbound(objective, 0., 1., args=(top,))
        u_bot = so.fminbound(objective, 0., 1., args=(bot,))

        return u_top, u_bot

    @property
    def center(self):
        """ Defines the Point where the C-mesh should transform into an H-mesh for maximum orthogonality of the mesh.
        The location is defined by the average x-value of the top and bottom maxima as obtained by
        :py:meth:`get_maxima`. Furthermore, it is coincident with the y-axis.

        :rtype: Point
        """

        u_top, u_bot = self.get_maxima()
        x_top, x_bot = self.curve['top'].point_at_parameter(u_top).x, self.curve['bot'].point_at_parameter(u_bot).x
        return Point((x_top + x_bot) / 2., 0)



    # def plot(self):
    #     """ Plots the Airfoil Geometry """
    #     top, bot = self.ordinates['top'], self.ordinates['bot']
    #     top, bot = [pnt.rotate(-self.angle) for pnt in top], [pnt.rotate(-self.angle) for pnt in bot]
    #     top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
    #     bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
    #     plt.plot(top_x, top_y)
    #     plt.plot(bot_x, bot_y)
    #     plt.axis([0, 1, -0.5, 0.5])
    #     plt.show()
    #     return None

    def get_ordinates(self):
        """ Retrieves the top and bottom coordinates of the airfoil. Both set of ordinates run from LE to TE.

        :rtype: dict
        """
        top, bot = self.ordinates['top'], self.ordinates['bot']
        top_x, top_y = [pnt.x for pnt in top], [pnt.y for pnt in top]
        bot_x, bot_y = [pnt.x for pnt in bot], [pnt.y for pnt in bot]
        return {'top': (top_x, top_y), 'bot': (bot_x, bot_y)}

    def read_cp(self, filename=None, extension='_cp.dat'):
        """ Reads airfoil ordinates from .dat file """
        filename = filename if filename is not None else os.path.join(DIRS['DATA_DIR'], 'pressure',
                                                                      self.__name__ + extension)
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

    def plot_cp(self):
        fig = plt.figure('{}PressureDistribution'.format(self.__name__))
        plt.style.use('tudelft')
        cp = self.read_cp()
        top_x, top_cp = [line[0] for line in cp['top']], [line[1] * -1. for line in cp['top']]
        bot_x, bot_cp = [line[0] for line in cp['bot']], [line[1] * -1. for line in cp['bot']]
        plt.plot(top_x, top_cp, label='Top Surface')
        plt.plot(bot_x, bot_cp, label='Bottom Surface')
        plt.axis([-0.1, 1.1, 1.5, -2])
        plt.legend()
        plt.xlabel(r'Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel(r'Pressure Coefficient [-]')
        plt.title(r'{} Pressure Distribution'.format(self.__name__))
        plt.show()

    def plot_airfoil(self):
        fig = plt.figure('{}Airfoil'.format(self.__name__))
        plt.style.use('tudelft')
        ord_dict = self.get_ordinates()
        top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
        plt.plot(top_x, top_y, label='Top Surface', marker='.')
        plt.plot(bot_x, bot_y, label='Bottom Surface', marker='.')

        control_u = np.linspace(0, 1, 100)
        top_pnts = [self.curve['top'].point_at_parameter(u) for u in control_u]
        bot_pnts = [self.curve['bot'].point_at_parameter(u) for u in control_u]

        top_x, top_y = [[getattr(pnt, key) for pnt in top_pnts] for key in ('x', 'y')]
        bot_x, bot_y = [[getattr(pnt, key) for pnt in bot_pnts] for key in ('x', 'y')]

        plt.plot(top_x, top_y, linewidth=0.5, linestyle='-.', label='Top Spline')
        plt.plot(bot_x, bot_y, linewidth=0.5, linestyle='-.', label='Bottom Spline')

        plt.xlabel('Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel('Normalized Thickness (t/c) [-]')
        plt.title('{} Airfoil Shape'.format(self.__name__))
        plt.legend()
        plt.axis([0, 1, -0.5, 0.5])
        plt.show()


if __name__ == '__main__':
    obj = Airfoil(angle=2.31)
    obj.plot_airfoil()
    obj.plot_cp()
    obj.write_dat()
    print(obj.get_maxima())
    # lines2 = obj.read_cp()
    # obj.plot_cp()
    # print(lines2)
