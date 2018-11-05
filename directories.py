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

""" directories.py is a file containing the function get_dir which allows the user to quickly call a directory within
the project folder, also for convenience the packages os and sys are imported when directories.py is imported with
the * specifier. Finally the dictionary DIRS contains common directories so as to avoid multiple calls to get_dir.
Finally since the entries in DIRS are outputs of get_dir the inherent directory checking is also present. Thus an
invalid directory will raise errors"""

import os
import sys

__all__ = ["get_dir", "DIRS", "os", "sys"]

# TODO Re-organize this to be a class structure if needed

# TODO Maybe re-write to use os.getcwd()


def get_dir(folder_name=None):
    """get_dir returns the top-level directory of the package as an absolute path if :attr:`folder_name` is not
    specified [1]. If an exiting sub directory is specified as :type:`str` into the field :attr:`folder_name` then the
    return of get_dir will be absolute path to this sub directory [2]. Usage with file names inside a directory is also
    possible, see example below [3]

        :param folder_name: The name of a folder, file, or relative path
        :type folder_name: basestring

        :return: The absolute path to the root directory or, if specified, to a sub directory within the root
        :rtype: unicode

        [1] Obtaining Root Directory:

        >>> get_dir() # This will return the absolute path to root directory
        C:/Python27/KBE

        [2] Obtaining a Sub-Directory:

        >>> get_dir('icons') # This will return the absolute path to the subdirectory /icons
        C:/Python27/KBE\icons

        [3] Obtaining File-Directory:

        >>> get_dir('user/userinput.xlsx') # This will return the absolute path to the file userinput.xlsx
        C:/Python27/KBE\user\userinput.xlsx
    """

    encoding = sys.getfilesystemencoding()  # A variable that returns encoding of the user's machine

    if hasattr(sys, "frozen"):  # Checks if the user is running through an .exe or from Python, Refer to is_frozen definition above
        root = os.path.join(os.path.dirname(unicode(sys.executable, encoding)),
                            "KBE")
    else:
        root = os.path.dirname(unicode(__file__, encoding))

    if folder_name is None:  # Checks if user has specified a value for field :attr:`folder_name`
        return root
    else:
        if isinstance(folder_name, str) or isinstance(folder_name, unicode):  # Check if folder_name has valid input
            subdir = os.path.join(root, folder_name)
            if os.path.isdir(subdir) or os.path.isfile(subdir):  # Check to see if folder_name is a valid path or file
                return subdir
            else:
            # TODO Properly distinguish between folder and file type, a folder named '2.0' will be treated as a file
                if subdir.find('.') != -1:  # Error handling to see if user was looking for a file or directory
                    raise NameError('Specified file %s does not exist' % subdir)
                else:
                    raise NameError('Specified directory %s does not exist' % subdir)
        else:
            raise TypeError('Please enter a valid string or unicode path into folder_name, %s is %s'
                            % (folder_name, type(folder_name)))


DIRS = {'DATA_DIR': get_dir('data')}

if __name__ == '__main__':
    print get_dir('user')
