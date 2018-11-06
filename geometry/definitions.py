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

from math import sqrt
from timeit import default_timer as timer
import numpy as np
import scipy.interpolate as si


class Point(object):

    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z=0.0):
        """ Creates a point tuple, enabling some built in methods for rotation and measuring distance

        :param float x: X-coordinate
        :param float y: Y-coordinate
        :param float z: Z-coordinate (Optional: If not provided points will be on XY plane)
        """
        self.x, self.y, self.z = float(x), float(y), float(z)

    def distance(self, other):
        """ Computes the distance from one point to another.

        :param Point other: Other point to compute distance to

        :return: Distance from ``self`` to ``other``
        :rtype: float
        """
        try:
            d = sqrt(sum([(getattr(self, key) - getattr(other, key))**2 for key in self.__slots__]))
            return d
        except AttributeError:
            raise AttributeError('Input must be a valid Point Instance')

    def rotate(self, angle):
        """ Rotates about the reference ``Point(0, 0, 0)`` """
        # TODO make more axis possible, currently only z-axis for AoA of airfoil
        a = np.radians(angle)

        rotate_z = np.matrix([[np.cos(a), -np.sin(a), 0],
                              [np.sin(a), np.cos(a), 0],
                              [0, 0, 1]])

        if angle != 0.0:
            rotated = rotate_z * np.matrix([self.x, self.y, self.z]).T
            return Point(rotated[0], rotated[1], rotated[2])
        else:
            return self

    def translate(self, vector):
        if isinstance(vector, Vector):
            return Point(*(np.matrix([self.x, self.y, self.z]).T + np.matrix([vector.x, vector.y, vector.z]).T))
        else:
            raise TypeError("`{}` is not a valid Vector".format(vector))

    def __repr__(self):
        return '<{}({}, {}, {}) object at {}>'.format(self.__class__.__name__, self.x, self.y, self.z, hex(id(self)))

    def __sub__(self, other):
        return None

    def __neg__(self):
        return self.__class__(*[-getattr(self, key) for key in self.__slots__])

    def __eq__(self, other):
        if isinstance(other, Point):
            return all([True if getattr(self, key) == getattr(other, key) else False for key in self.__slots__])
        else:
            raise TypeError("`{}` is not a valid Point".format(other))

    def __getitem__(self, item):
        try:
            return getattr(self, self.__slots__[item])
        except IndexError or KeyError as error:
            raise error


class Vector(Point):

    def __init__(self, x, y, z=0.0):
        """ Creates a vector, enabling some built in methods for projection

        :param float x: X-component
        :param float y: Y-component
        :param float z: Z-component (Optional: If not provided vector will be on XY plane)
        """
        super(Vector, self).__init__(x, y, z)

    def __mul__(self, other):
        """ Implements vector multiplication vector * other
        :rtype: Vector
        """
        try:
            return Vector(*(np.matrix([self.x, self.y, self.z]).T * other))
        except Exception as e:
            raise e

    def cross(self, other):
        x = (self.y*other.z - self.z*other.y)
        y = -(self.x*other.z - self.z*other.x)
        z = (self.x*other.y - self.y*other.x)
        return Vector(x, y, z)

    def magnitude(self):
        return sqrt(sum([getattr(self, key)**2 for key in self.__slots__]))

    def normalize(self):
        mag = self.magnitude()
        return Vector(*[getattr(self, key) / mag for key in self.__slots__])


class Curve(object):

    def __init__(self, built_from, degree=3):
        """ Constructs a 2D B-spline from a list of :py:class:`Point` making use of the SciPy spline functions

        :param list[Point] built_from: Specifies the points the curve should be built-from
        :param int degree: Degree of the spline used to fit to the data
        """
        self.__cache__ = {}
        self.built_from = built_from
        self.degree = degree

    @property
    def spline(self):
        """ Cached property of the B-Spline Curve for easy access """

    @spline.getter
    def spline(self):
        """ Takes care of caching the constructed B-Spline curve """
        if 'spline' in self.__cache__.keys():
            return self.__cache__['spline']
        else:
            _x, _y = [pnt.x for pnt in self.built_from], [pnt.y for pnt in self.built_from]

            # TODO: Allow user specification of smoothing
            # Smoothing hardcoded for now s = 0.0
            _spline, u, = si.splprep((_x, _y), s=0.0, k=self.degree)  # Ignore unpacking warning, it is due to Numpy doc
            self.__cache__['spline'] = _spline
            return _spline

    def tangent(self, u):
        """ Returns the curve unit tangent vector evaluated at the parameter ``u`` """
        return Vector(*si.splev(u, self.spline, der=1)).normalize()

    def normal(self, u):
        """ Returns the curve unit normal vector evaluated at the parameter ``u``

        .. Note:: Normal is defined as the cross-product w.r.t the negative z-axis, thus it is 90 deg \n
        counter-clockwise from the tangent vector.

        :rtype: Vector
        """
        return self.tangent(u).cross(Vector(0, 0, -1))

    def point_at_parameter(self, u):
        """ Returns a point on the curve at a parameter ``u``

        :rtype: Point
        """
        return Point(*si.splev(u, self.spline, der=0))


if __name__ == '__main__':
    pt1 = Point(1., 0., 0)
    pt2 = Point(0, 0.5, 0)
    vec = Vector(1, 0, 0)
    print(vec.cross(Vector(0, 1, 0)))
    start = timer()
    distance = pt1.distance(pt2)
    end = timer()
    print(distance)
    print('Time = {}'.format(end-start))
    print(vec[0])
    print(-vec)


