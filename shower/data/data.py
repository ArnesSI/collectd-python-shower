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

from ..base import ShowerBase
from ..exceptions import ShowerConfigException


class Data(ShowerBase):
    def __init__(self, conf):
        super(Data, self).__init__()
        self.name = None
        self.style = None
        self.plugininstance = None
        self.types = []
        self.table = False
        self.instance = None
        self.result = {}
        self._from_conf(conf)
        self._validate()

    def _from_conf(self, conf):
        self.name = conf.values[0]
        for node in conf.children:
            key = node.key.lower()
            if key in ['style', 'plugininstance', 'instance']:
                setattr(self, key, str(node.values[0]))
            elif key in ['types']:
                setattr(self, key, node.values)
            elif key in ['table', 'verbose', 'debug']:
                setattr(self, key, bool(node.values[0]))

    def _validate(self):
        if not self.name:
            raise ShowerConfigException('Unnamed Data section')

    def parse(self, output):
        raise NotImplementedError()
