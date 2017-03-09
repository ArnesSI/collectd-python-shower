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

from .base import ShowerBase
from .exceptions import ShowerConfigException


class Data(ShowerBase):
    def __init__(self, conf, verbose=False):
        super(Data, self).__init__(verbose)
        self.name = str(conf.values[0])
        self.command = None
        self._from_conf(conf)
        self._validate()

    def _from_conf(self, conf):
        for node in conf.children:
            key = node.key.lower()
            if key in ['command']:
                setattr(self, key, str(node.values[0]))

    def _validate(self):
        if not self.name:
            raise ShowerConfigException('Unnamed Data config section')
        if not self.command:
            raise ShowerConfigException('Mussing Command in Data "{}" section'.format(self.name))

    def parse(self, output):
        return None

# vim: tabstop=4 shiftwidth=4 expandtab
