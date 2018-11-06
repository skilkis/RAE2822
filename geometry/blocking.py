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

from geometry.definitions import Vector, Point
import scipy.interpolate as si
import scipy.optimize as so
from matplotlib import pyplot as plt
from math import atan, atan2, degrees, radians


class Blocking(object):

    def __init__(self, domain_in=None, le_angle=60):
        self.domain_in = domain_in
        self.airfoil_in = self.domain_in.airfoil_in
        self.le_angle = le_angle
        self.le_zone = self.find_le_zone(self.le_angle)
        self.crv_top = self.airfoil_in.curve['top']
        self.crv_bot = self.airfoil_in.curve['bot']

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

    @property
    def pt_1(self):
        u_top, _ = self.airfoil_in.get_maxima()
        return self.crv_top.point_at_parameter(u_top)

    @property
    def pt_2(self):
        return self.crv_top.point_at_parameter(0.7)

    @property
    def pt_2_mid(self):
        return self.pt_2.translate(self.airfoil_in.curve[])

    @property
    def pt_3(self):
        return self.airfoil_in.trailing_edge

    @property
    def pt_6(self):
        _, u_bot = self.airfoil_in.get_maxima()
        return self.crv_bot.point_at_parameter(u_bot)

    @property
    def pt_7(self):
        return self.crv_bot.point_at_parameter(self.le_zone['bot'])

    @property
    def pt_8(self):
        return self.crv_top.point_at_parameter(self.le_zone['top'])



    def plot(self, angle=60.):
        fig = plt.figure('{}Airfoil'.format(self.airfoil_in.__name__))
        plt.style.use('tudelft')
        ord_dict = self.airfoil_in.get_ordinates()
        top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
        plt.plot(top_x, top_y, label='Top Surface')
        plt.plot(bot_x, bot_y, label='Bottom Surface')

        # crv_top, crv_bot = self.airfoil_in.curve['top'], self.airfoil_in.curve['bot']

        # u_top, u_bot = self.airfoil_in.get_maxima()
        #
        # # Tangent Points
        # top_pnt = crv_top.point_at_parameter(u_top)
        # bot_pnt = crv_bot.point_at_parameter(u_bot)
        #
        plt.scatter(self.pt_1.x, self.pt_1.y)
        plt.scatter(self.pt_2.x, self.pt_2.y)
        plt.scatter(self.pt_3.x, self.pt_3.y)
        #
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
        plt.axis([-0.5, 2.0, -1.25, 1.25])
        plt.show()


if __name__ == '__main__':
    from geometry.airfoil import Airfoil
    from geometry.domain import Domain
    obj = Blocking(Domain(Airfoil(angle=2.31), upstream=13., top=13., bottom=13., wake=20.))
    print(obj.find_le_zone(60))
    obj.plot(50)
    #
    # x = Vector(1, 0, 0)
    # z = Vector(0, 0, -1)
    # print(x.cross(z))
    # print(obj.get_normal())
