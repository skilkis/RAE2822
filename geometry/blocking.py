from geometry.definitions import Vector, Point

import scipy.interpolate as si
import scipy.optimize as so
from matplotlib import pyplot as plt
from math import atan, atan2, degrees, radians


class Blocking(object):

    def __init__(self, airfoil_in):
        self.airfoil_in = airfoil_in

    def get_normal(self):

        _, _, top_t, bot_t = self.airfoil_in.get_maxima()
        top_tangent, bot_tangent = Vector(top_t[0], top_t[1], 0), Vector(bot_t[0], bot_t[1], 0)

        top_normal, bot_normal = top_tangent.cross(Vector(0, 0, -1)), bot_tangent.cross(Vector(0, 0, -1))
        return top_normal.normalize(), bot_normal.normalize()

    def find_le_zone(self, angle):
        top, bot = self.airfoil_in.spline

        def objective(u, *args):
            """ Returns the angle formed between the x-axis and the normal vector in the 1st quadrant. This is done
            to ensure that the LE refinement zone has an equal angle all the way up to the airfoil surface for optimum
            orthogonality of the mesh. """
            spline, target_angle = args
            tangent = Vector(*si.splev(u, spline, der=1))
            normal = tangent.cross(Vector(0, 0, -1))
            return degrees(atan(abs(normal.y/normal.x))) - target_angle

        u_top = so.brentq(objective, 0., 0.5, args=(top, angle))
        u_bot = so.brentq(objective, 0., 0.3, args=(bot, angle))

        return u_top, u_bot

        # top_max, bot_max = si.splev(u_top, top, der=0), si.splev(u_bot, bot, der=0)
        # return u_top, u_bot, si.splev(u_top, top, der=1), si.splev(u_bot, top, der=1)

    def plot(self, angle=60.):
        fig = plt.figure('{}Airfoil'.format(self.airfoil_in.__name__))
        plt.style.use('tudelft')
        ord_dict = self.airfoil_in.get_ordinates()
        top_x, top_y, bot_x, bot_y = (ord_dict['top'] + ord_dict['bot'])
        plt.plot(top_x, top_y, label='Top Surface')
        plt.plot(bot_x, bot_y, label='Bottom Surface')

        top_normal, bot_normal = self.get_normal()
        u_top, u_bot, _, _ = self.airfoil_in.get_maxima()

        # Tangent Points
        spline_top, spline_bot = self.airfoil_in.spline
        top_pnt = Point(*si.splev(u_top, spline_top, der=0))
        bot_pnt = Point(*si.splev(u_bot, spline_bot, der=0))

        plt.scatter(top_pnt.x, top_pnt.y)
        plt.scatter(bot_pnt.x, bot_pnt.y)

        top_pnt = top_pnt.translate(top_normal * 0.3)
        bot_pnt = bot_pnt.translate(bot_normal * - 0.3)

        plt.scatter(top_pnt.x, top_pnt.y)
        plt.scatter(bot_pnt.x, bot_pnt.y)

        # 50 Degree LE Refinement Zone
        u_top, u_bot = self.find_le_zone(angle)

        # Top LE Refinement Zone Points
        top_pnt = Point(*si.splev(u_top, spline_top, der=0))
        plt.scatter(top_pnt.x, top_pnt.y)
        tangent = Vector(*si.splev(u_top, spline_top, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        top_pnt = top_pnt.translate(normal * 0.3)
        plt.scatter(top_pnt.x, top_pnt.y)

        # Bottom LE Refinement Points
        bot_pnt = Point(*si.splev(u_bot, spline_bot, der=0))
        plt.scatter(bot_pnt.x, bot_pnt.y)
        tangent = Vector(*si.splev(u_bot, spline_bot, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        bot_pnt = bot_pnt.translate(normal * -0.3)
        plt.scatter(bot_pnt.x, bot_pnt.y)

        # Bottom Mid-Back Refinement Points
        bot_pnt = Point(*si.splev(0.7, spline_bot, der=0))
        plt.scatter(bot_pnt.x, bot_pnt.y)
        tangent = Vector(*si.splev(0.7, spline_bot, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        bot_pnt = bot_pnt.translate(normal * -0.3)
        plt.scatter(bot_pnt.x, bot_pnt.y)

        # Top Mid-Back Refinement Zone Points
        top_pnt = Point(*si.splev(0.7, spline_top, der=0))
        plt.scatter(top_pnt.x, top_pnt.y)
        tangent = Vector(*si.splev(0.7, spline_top, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        top_pnt = top_pnt.translate(normal * 0.3)
        plt.scatter(top_pnt.x, top_pnt.y)

        # TE Refinement Zone Points
        top_pnt = Point(*si.splev(1.0, spline_top, der=0))
        plt.scatter(top_pnt.x, top_pnt.y)
        tangent = Vector(*si.splev(1.0, spline_top, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        top_pnt = top_pnt.translate(normal * 0.3)
        plt.scatter(top_pnt.x, top_pnt.y)
        bot_pnt = Point(*si.splev(1.0, spline_bot, der=0))
        plt.scatter(bot_pnt.x, bot_pnt.y)
        tangent = Vector(*si.splev(1.0, spline_bot, der=1))
        normal = tangent.cross(Vector(0, 0, -1)).normalize()
        bot_pnt = bot_pnt.translate(normal * -0.3)
        plt.scatter(bot_pnt.x, bot_pnt.y)

        # TE Farfield Point
        te_pnt = Point(*si.splev(1.0, spline_top, der=0))
        plt.scatter(te_pnt.x, te_pnt.y)
        tangent = Vector(*si.splev(1.0, spline_top, der=1)).normalize()
        te_pnt = te_pnt.translate(tangent * 0.5)
        plt.scatter(te_pnt.x, te_pnt.y)

        te_pnt_top = te_pnt.translate(tangent.cross(Vector(0, 0, -1)) * 0.3)
        plt.scatter(te_pnt_top.x, te_pnt_top.y)

        te_pnt_bot = te_pnt.translate(tangent.cross(Vector(0, 0, -1)) * -0.3)
        plt.scatter(te_pnt_bot.x, te_pnt_bot.y)

        plt.xlabel('Normalized Location on Airfoil Chord (x/c) [-]')
        plt.ylabel('Normalized Thickness (t/c) [-]')
        plt.title('{} Airfoil Shape'.format(self.airfoil_in.__name__))
        plt.legend()
        plt.axis([-0.5, 2.0, -1.25, 1.25])
        plt.show()


if __name__ == '__main__':
    from geometry.airfoil import Airfoil
    obj = Blocking(Airfoil(angle=2.31))
    print(obj.find_le_zone(60))
    obj.plot(50)
    #
    # x = Vector(1, 0, 0)
    # z = Vector(0, 0, -1)
    # print(x.cross(z))
    # print(obj.get_normal())
