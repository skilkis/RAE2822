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
        return '<Point({}, {}, {}) object at {}>'.format(self.x, self.y, self.z, hex(id(self)))

    def __sub__(self, other):
        return None

    def __eq__(self, other):
        if isinstance(other, Point):
            return all([True if getattr(self, key) == getattr(other, key) else False for key in self.__slots__])
        else:
            raise TypeError("`{}` is not a valid Point".format(other))


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

    def __repr__(self):
        return '<Vector({}, {}, {}) object at {}>'.format(self.x, self.y, self.z, hex(id(self)))

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


