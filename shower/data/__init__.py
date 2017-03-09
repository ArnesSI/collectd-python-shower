# -*- coding: utf-8 -*-
########################################################################
#
# MIT License
#
# Copyright (c) 2017 Matej Vadnjal <matej@arnes.si>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
########################################################################

from ..exceptions import ShowerConfigException
from .regex import DataRegex
from .template import DataTextFSM

def make_data(conf):
    style = get_style(conf)
    if not style:
        raise ShowerConfigException('Missing Style in Data "{}" section'.format(conf.values[0]))
    elif style == 'regex':
        return DataRegex(conf)
    elif style == 'textfsm':
        return DataTextFSM(conf)
    else:
        raise ShowerConfigException('Unsupported Style "{}" in Data "{}" section'.format(style, conf.values[0]))


def get_style(conf):
    for node in conf.children:
        key = node.key.lower()
        if key == 'style':
            return node.values[0].lower()
    return None
