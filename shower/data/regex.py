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

import re
from ..exceptions import ShowerConfigException
from .data import Data


class DataRegex(Data):
    def __init__(self, conf):
        self.command = None
        self.regex = None
        super(DataRegex, self).__init__(conf)

    def _from_conf(self, conf):
        super(DataRegex, self)._from_conf(conf)
        for node in conf.children:
            key = node.key.lower()
            if key == 'command':
                setattr(self, key, str(node.values[0]))
            elif key == 'regex':
                setattr(self, key, re.compile(node.values[0]))

    def _validate(self):
        super(DataRegex, self)._validate()
        if not self.command:
            raise ShowerConfigException('Missing Command in Data "{}" section'.format(self.name))
        if not self.regex:
            raise ShowerConfigException('Missing Regex in Data "{}" section'.format(self.name))

    def parse(self, output):
        if self.table:
            parsed = self._parse_by_line(output)
        else:
            parsed = [self._parse_line(output)]
        self.log('info', str(parsed))

    def _parse_by_line(self, output):
        parsed = []
        for line in output.split('\n'):
            parsed.append(self._parse_line(line))
        return parsed

    def _parse_line(self, line):
        m = self.regex.search(line)
        if m:
            return m.groupdict()
        else:
            return None
