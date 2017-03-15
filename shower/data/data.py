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

import collectd
from ..base import ShowerBase
from ..exceptions import ShowerConfigException
from .. import formatters


class Data(ShowerBase):
    def __init__(self, conf):
        super(Data, self).__init__()
        self.name = None
        self.style = None
        self.plugininstance = None
        self.types = []
        self.table = False
        self.typeinstance = None
        self.formatters = {}
        self._from_conf(conf)
        self._validate()

    def _from_conf(self, conf):
        self.name = conf.values[0]
        for node in conf.children:
            key = node.key.lower()
            if key in ['style', 'plugininstance', 'typeinstance']:
                setattr(self, key, str(node.values[0]))
            elif key in ['types']:
                setattr(self, key, [t.lower() for t in node.values])
            elif key in ['table', 'verbose', 'debug']:
                setattr(self, key, bool(node.values[0]))
            elif key == 'formatter':
                self.formatters[node.values[0]] = node.values[1]

    def _validate(self):
        if not self.name:
            raise ShowerConfigException('Unnamed Data section')

    def parse(self, output):
        raise NotImplementedError()

    def format_metric(self, typ, instance, value):
        if typ in self.formatters.keys():
            func = getattr(formatters, self.formatters[typ])
        else:
            func = float
        return func(value)

    def dispach(self, host, results):
        for type_instance, result in results.items():
            self._dispach_result(host, type_instance, result)

    def _dispach_result(self, host, type_instance, result):
        for typ, value in result.items():
            value = self.format_metric(typ, type_instance, value)
            val = collectd.Values()
            val.host = host.name
            val.plugin = self.plugin_name
            val.type = typ
            val.values = [value]
            if self.plugininstance:
                val.plugin_instance = self.plugininstance
            if self.table:
                val.type_instance = type_instance
            self.log('info', repr(val))
            val.dispatch()
