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
from directories import DIRS
from geometry.definitions import Point, Vector
import scipy.optimize as so
from matplotlib import pyplot as plt
from math import atan, degrees, tan


class Blocking(object):

    def __init__(self, domain_in=None, le_angle=35, refine_distance=0.3, x_value=0.01):
        self.domain_in = domain_in
        self.airfoil_in = self.domain_in.airfoil_in
        self.crv_top = self.airfoil_in.curve['top']
        self.crv_bot = self.airfoil_in.curve['bot']
        self.le_angle = le_angle
        self.le_zone = self.find_le_zone(le_angle)
        self.refine_distance = refine_distance

    @property
    def default_directory(self):
        return os.path.join(DIRS['DATA_DIR'], 'geom')

    def find_le_zone(self, angle):
        top, bot = self.crv_top, self.crv_bot

        def objective(u, *args):
            """ Returns the angle formed between the x-axis and the normal vector in the 1st quadrant. This is done
            to ensure that the LE refinement zone has an equal angle all the way up to the airfoil surface for optimum
            orthogonality of the mesh. """
            crv, target_angle = args
            normal = crv.normal(u)
            return degrees(atan(abs(normal.y/normal.x))) - target_angle

        u_top = so.brentq(objective, 0., 0.5, args=(top, angle))
        u_bot = so.brentq(objective, 0., 0.3, args=(bot, angle))

        return {'top': u_top, 'bot': u_bot}

    # def find_le_zone(self, x_value):
    #     top, bot = self.crv_top, self.crv_bot
    #
    #     def objective(u, *args):
    #         """ Returns the error between the requested x_value and the current x value at u """
    #         crv, target_x = args
    #         point = crv.point_at_parameter(u)
    #         return point.x - target_x
    #
    #     u_top = so.brentq(objective, 0., 0.5, args=(top, x_value))
    #     u_bot = so.brentq(objective, 0., 0.5, args=(bot, x_value))
    #
    #     return {'top': u_top, 'bot': u_bot}

    @property
    def pt_1(self):
        u_top, _ = self.airfoil_in.get_maxima()
        return self.crv_top.point_at_parameter(u_top)

    @property
    def pt_1_top(self):
        u_top, _ = self.airfoil_in.get_maxima()
        return self.pt_1.translate(self.crv_top.normal(u_top) * self.refine_distance)

    @property
    def pt_2(self):
        return self.airfoil_in.trailing_edge

    @property
    def pt_2_top(self):
        return self.pt_2.translate(self.crv_top.normal(1.0)*self.refine_distance)

    @property
    def pt_2_bot(self):
        return self.pt_2.translate(self.crv_bot.normal(1.0) * - self.refine_distance)

    # @property
    # def pt_4(self):
    #     return self.pt_2.translate(self.crv_top.tangent(1.0) * 0.1)
    #
    # @property
    # def pt_4_bot(self):
    #     return self.pt_4.translate(self.crv_bot.normal(1.0) * -self.refine_distance)
    #
    # @property
    # def pt_4_top(self):
    #     return self.pt_4.translate(self.crv_top.normal(1.0) * self.refine_distance)
    #
    # @property
    # def pt_5(self):
    #     return self.crv_bot.point_at_parameter(0.7)
    #
    # @property
    # def pt_5_bot(self):
    #     return self.pt_5.translate(self.crv_bot.normal(0.7) * -self.refine_distance)

    @property
    def pt_3(self):
        _, u_bot = self.airfoil_in.get_maxima()
        return self.crv_bot.point_at_parameter(u_bot)

    @property
    def pt_3_bot(self):
        _, u_bot = self.airfoil_in.get_maxima()
        return self.pt_3.translate(self.crv_bot.normal(u_bot) * -self.refine_distance)

    @property
    def pt_4(self):
        return self.crv_bot.point_at_parameter(self.le_zone['bot'])

    @property
    def pt_4_bot(self):
        return self.pt_4.translate(self.crv_bot.normal(self.le_zone['bot']) * -self.refine_distance)

    @property
    def pt_5(self):
        return self.crv_top.point_at_parameter(self.le_zone['top'])

    @property
    def pt_5_top(self):
        return self.pt_5.translate(self.crv_top.normal(self.le_zone['top']) * self.refine_distance)

    @property
    def pt_le_proj(self):
        return self.airfoil_in.leading_edge.translate(Vector(-self.refine_distance, 0, 0))

    def plot(self):
        fig = plt.figure('{}Airfoil'.format(self.airfoil_in.__name__))
        # plt.style.use('tudelft')
        ord_dict = self.airfoil_in.get_ordinates()
        top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
        plt.plot(top_x, top_y, label='Top Surface')
        plt.plot(bot_x, bot_y, label='Bottom Surface')

        plt.scatter(self.pt_1.x, self.pt_1.y)
        plt.scatter(self.pt_1_top.x, self.pt_1_top.y)

        plt.scatter(self.pt_2.x, self.pt_2.y)
        plt.scatter(self.pt_2_top.x, self.pt_2_top.y)
        plt.scatter(self.pt_2_bot.x, self.pt_2_bot.y)

        plt.scatter(self.pt_3.x, self.pt_3.y)
        plt.scatter(self.pt_3.x, self.pt_3.y)
        plt.scatter(self.pt_3_bot.x, self.pt_3_bot.y)

        plt.scatter(self.pt_4.x, self.pt_4.y)
        plt.scatter(self.pt_4_bot.x, self.pt_4_bot.y)

        plt.scatter(self.pt_5.x, self.pt_5.y)
        plt.scatter(self.pt_5_top.x, self.pt_5_top.y)

        plt.scatter(self.airfoil_in.leading_edge.x, self.airfoil_in.leading_edge.y)
        plt.scatter(self.pt_le_proj.x, self.pt_le_proj.y)

        # Calculating Pt_2 Domain Projection
        pt_2 = self.pt_2_top
        y = self.domain_in.pt_2.y - self.pt_2_top.y
        print(y)
        v_norm = self.crv_top.normal(1.0)
        print(v_norm)
        x = y / (v_norm.y / v_norm.x)
        print(degrees(v_norm.y / v_norm.x))

        plt.scatter(self.pt_2_top.x + x, self.domain_in.pt_2.y)





        # plt.scatter(self.pt_3.x, self.pt_3.y)
        # plt.scatter(self.pt_3_top.x, self.pt_3_top.y)
        # plt.scatter(self.project(self.pt_3_top, 'top').x, self.project(self.pt_3_top, 'top').y)
        # plt.scatter(self.pt_3_bot.x, self.pt_3_bot.y)
        # plt.scatter(self.project(self.pt_3_bot, 'bot').x, self.project(self.pt_3_bot, 'bot').y)
        #
        # plt.scatter(self.pt_4.x, self.pt_4.y)
        # plt.scatter(self.project(self.pt_4, 'wake').x, self.project(self.pt_4, 'wake').y)
        # plt.scatter(self.pt_4_top.x, self.pt_4_top.y)
        # plt.scatter(self.project(self.pt_4_top, 'top').x, self.project(self.pt_4_top, 'top').y)
        # plt.scatter(self.project(self.pt_4_top, 'wake').x, self.project(self.pt_4_top, 'wake').y)
        # plt.scatter(self.pt_4_bot.x, self.pt_4_bot.y)
        # plt.scatter(self.project(self.pt_4_bot, 'bot').x, self.project(self.pt_4_bot, 'bot').y)
        # plt.scatter(self.project(self.pt_4_bot, 'wake').x, self.project(self.pt_4_bot, 'wake').y)
        #
        # plt.scatter(self.pt_5.x, self.pt_5.y)
        # plt.scatter(self.pt_5_bot.x, self.pt_5_bot.y)
        # plt.scatter(self.project(self.pt_5_bot, 'bot').x, self.project(self.pt_5_bot, 'bot').y)
        #
        # plt.scatter(self.pt_6.x, self.pt_6.y)
        # plt.scatter(self.pt_6_bot.x, self.pt_6_bot.y)
        #
        # plt.scatter(self.pt_7.x, self.pt_7.y)
        # plt.scatter(self.pt_7_bot.x, self.pt_7_bot.y)
        #
        # plt.scatter(self.airfoil_in.leading_edge.x, self.airfoil_in.leading_edge.y)
        #
        # plt.scatter(self.pt_le_proj.x, self.pt_le_proj.y)
        #
        # plt.scatter(self.pt_8.x, self.pt_8.y)
        # plt.scatter(self.pt_8_top.x, self.pt_8_top.y)
        # plt.scatter(self.pt_4_top_proj.x, self.pt_4_top_proj.y)

        # top_pnt = top_pnt.translate(crv_top.normal(u_top) * 0.3)
        # bot_pnt = bot_pnt.translate(crv_bot.normal(u_bot) * - 0.3)
        #
        # plt.scatter(top_pnt.x, top_pnt.y)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        #
        # # 50 Degree LE Refinement Zone
        # u_top, u_bot = self.find_le_zone(angle)
        #
        # # Top LE Refinement Zone Points
        # top_pnt = crv_top.point_at_parameter(u_top)
        # plt.scatter(top_pnt.x, top_pnt.y)
        # top_pnt = top_pnt.translate(crv_top.normal(u_top) * 0.3)
        # plt.scatter(top_pnt.x, top_pnt.y)
        #
        # # Bottom LE Refinement Zone Points
        # bot_pnt = crv_bot.point_at_parameter(u_top)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        # bot_pnt = bot_pnt.translate(crv_bot.normal(u_bot) * -0.3)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        #
        # # Top Mid-Back Refinement Points
        # top_pnt = crv_top.point_at_parameter(0.7)
        # plt.scatter(top_pnt.x, top_pnt.y)
        # top_pnt = top_pnt.translate(crv_top.normal(0.7) * 0.3)
        # plt.scatter(top_pnt.x, top_pnt.y)
        #
        # # Bottom Mid-Back Refinement Points
        # bot_pnt = crv_bot.point_at_parameter(0.7)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        # bot_pnt = bot_pnt.translate(crv_bot.normal(0.7) * -0.3)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        #
        # # TE Refinement Zone Points (Top/Bottom)
        # top_pnt = crv_top.point_at_parameter(1.0)
        # plt.scatter(top_pnt.x, top_pnt.y)
        # top_pnt = top_pnt.translate(crv_top.normal(1.0) * 0.3)
        # plt.scatter(top_pnt.x, top_pnt.y)
        #
        # bot_pnt = crv_bot.point_at_parameter(1.0)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        # bot_pnt = bot_pnt.translate(crv_bot.normal(1.0) * -0.3)
        # plt.scatter(bot_pnt.x, bot_pnt.y)
        #
        # # TE Farfield Point
        # te_pnt = crv_top.point_at_parameter(1.0)
        # plt.scatter(te_pnt.x, te_pnt.y)
        # te_pnt = te_pnt.translate(crv_top.tangent(1.0) * 0.5)
        # plt.scatter(te_pnt.x, te_pnt.y)
        #
        # te_pnt_top = te_pnt.translate(crv_top.normal(1.0) * 0.3)
        # plt.scatter(te_pnt_top.x, te_pnt_top.y)
        #
        # te_pnt_bot = te_pnt.translate(crv_bot.normal(1.0) * -0.3)
        # plt.scatter(te_pnt_bot.x, te_pnt_bot.y)
        #
        # center_pnt = self.airfoil_in.center
        # plt.scatter(center_pnt.x, center_pnt.y)

        plt.xlabel('Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel('Normalized Thickness (t/c) [-]')
        plt.title('{} Airfoil Shape'.format(self.airfoil_in.__name__))
        plt.legend()
        # plt.axis([-0.5, 2.0, -1.25, 1.25])
        plt.axis([self.domain_in.pt_5.x, self.domain_in.pt_2.x, self.domain_in.pt_3.y, self.domain_in.pt_2.y])
        plt.show()

    def project(self, point, side):
        if side == 'top':
            pt = Point(point.x, self.domain_in.pt_1.y, 0)
        elif side == 'wake':
            pt = Point(self.domain_in.pt_2.x, point.y, 0)
        elif side == 'bot':
            pt = Point(point.x, self.domain_in.pt_3.y, 0)
        else:
            raise ValueError('{} is not a valid side of the domain')
        return pt

    def write_dat(self, filename=None, extension='_BLOCKING.dat'):
        """ Writes modified airfoil ordinates to .dat file """
        name = self.airfoil_in.__name__
        filename = filename if filename is not None else os.path.join(self.default_directory, name + extension)

        def point_format(open_file, point):
            return open_file.write('  {:1.6f}  {:1.6f}  {:1.6f}\n'.format(point.x, point.y, point.z).replace('-0', '-'))

        with open(filename, 'w') as output:
            output.write('# {} AIRFOIL BLOCKING POINTS\n'.format(name))

            # # Airfoil Trailing Edge Mid
            # point_format(output, self.pt_2)
            # point_format(output, self.pt_4)
            # point_format(output, self.project(self.pt_4, 'wake'))
            #
            # # Airfoil Trailing Edge Top
            # point_format(output, self.pt_3_top)
            # point_format(output, self.project(self.pt_3_top, 'top'))
            # point_format(output, self.pt_4_top)
            # point_format(output, self.project(self.pt_4_top, 'wake'))
            # point_format(output, self.project(self.pt_4_top, 'top'))
            #
            # # Airfoil Trailing Edge Bottom
            # point_format(output, self.pt_3_bot)
            # point_format(output, self.project(self.pt_3_bot, 'bot'))
            # point_format(output, self.pt_4_bot)
            # point_format(output, self.project(self.pt_4_bot, 'wake'))
            # point_format(output, self.project(self.pt_4_top, 'top'))

            # Airfoil Trailing Edge
            point_format(output, self.project(self.pt_2, 'wake'))
            point_format(output, self.project(self.pt_2_top, 'wake'))

            # Airfoil Trailing Edge Upper Top Projection
            pt_2 = self.pt_2_top
            y = self.domain_in.pt_2.y - self.pt_2_top.y
            v_norm = self.crv_top.normal(1.0)
            x = y / (v_norm.y / v_norm.x)
            point_format(output, Point(self.pt_2.x + x, self.domain_in.pt_2.y, 0))
            print(degrees(v_norm.y / v_norm.x))

            point_format(output, self.project(self.pt_2_bot, 'wake'))
            point_format(output, self.project(self.pt_2_bot, 'bot'))

            # Airfoil Surface Points
            point_format(output, self.pt_1)
            point_format(output, self.pt_2)
            point_format(output, self.pt_3)
            point_format(output, self.pt_4)
            point_format(output, self.pt_5)

            # Airfoil Refinment Spline
            output.write(' {:d} 0\n'.format(9))
            point_format(output, self.pt_2_bot)
            point_format(output, self.pt_3_bot)
            point_format(output, self.pt_4_bot)
            point_format(output, self.pt_le_proj)
            point_format(output, self.pt_5_top)
            point_format(output, self.pt_1_top)
            point_format(output, self.pt_2_top)

            # # Segment 2-3
            # output.write(' {:d} 0\n'.format(2))
            # point_format(output, pt_2)
            # point_format(output, pt_3)
            #
            # # Segment 3-4
            # output.write(' {:d} 0\n'.format(2))
            # point_format(output, pt_3)
            # point_format(output, pt_4)
            #
            # # Segment 4-1
            # output.write(' {:d} 0\n'.format(3))
            # point_format(output, pt_4)
            # point_format(output, pt_5)
            # point_format(output, pt_1)


if __name__ == '__main__':
    from geometry.airfoil import Airfoil
    from geometry.domain import Domain
    obj = Blocking(Domain(Airfoil(angle=2.31), upstream=13., top=13., bottom=13., wake=20.))
    # obj.plot()
    obj.write_dat()
    #
    # x = Vector(1, 0, 0)
    # z = Vector(0, 0, -1)
    # print(x.cross(z))
    # print(obj.get_normal())
