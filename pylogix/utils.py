"""
   Copyright 2022 Dustin Roeder (dmroeder@gmail.com)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys

SO_BROADCAST = 6

def is_micropython():
    if hasattr(sys, 'implementation'):
        if sys.implementation.name == 'micropython':
            return True
        return False
    return False


def is_python3():
    if hasattr(sys.version_info, 'major'):
        if sys.version_info.major == 3:
            return True
        return False
    return False


def is_python2():
    if hasattr(sys.version_info, 'major'):
        if sys.version_info.major == 2:
            return True
        return False
    return False
