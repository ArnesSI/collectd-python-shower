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

import os
import re
from copy import deepcopy
from ..exceptions import ShowerConfigException
from .data import Data


class DataTextFSM(Data):
    def __init__(self, conf):
        self.template = None
        self.searchdirs = [os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'templates'))]
        self.template_fullpath = '' # full absolute path to the textfsm template
        self.command = None
        self.typeoverride = None
        self._textfsm = None
        super(DataTextFSM, self).__init__(conf)
        self._get_template_path()
        self._read_command()
        self._textfsm_init()

    def _from_conf(self, conf):
        super(DataTextFSM, self)._from_conf(conf)
        # get TemplateDir from parent conf
        for node in conf.parent.children:
            key = node.key.lower()
            if key == 'templatepath':
                self.searchdirs.extend(node.values)
        for node in conf.children:
            key = node.key.lower()
            if key in ['template', 'command', 'typeoverride']:
                setattr(self, key, str(node.values[0]))
            elif key == 'templatepath':
                self.searchdirs.extend(node.values)

    def _validate(self):
        super(DataTextFSM, self)._validate()
        if not self.template:
            raise ShowerConfigException('Missing Template in Data "{}" section'.format(self.name))

    def _get_template_path(self):
        if os.path.isabs(self.template):
            self.template_fullpath = self.template
        else:
            for searchdir in reversed(self.searchdirs):
                test_fullpath = os.path.join(searchdir, self.template)
                if os.path.isfile(test_fullpath):
                    self.template_fullpath = test_fullpath
                    break
        if not os.path.isfile(self.template_fullpath):
            raise ShowerConfigException('Template does not exist or is not readable "{}" in Data "{}"'.format(self.template_fullpath, self.name))

    def _read_command(self):
        if self.command:
            # don't search if set in collectd config file
            return
        with open(self.template_fullpath, 'r') as fh:
            for line in fh:
                if line.startswith('Value ') and not self.command:
                    raise ShowerConfigException('Command not found in TextFSM template "{}" in Data "{}"'.format(self.template_fullpath, self.name))
                m = re.search(r'^#\s*[Cc]ommand:\s+(.+?)\s*$', line)
                if m:
                    self.command = m.group(1)
        if not self.command:
            raise ShowerConfigException('Command not found in TextFSM template "{}" in Data "{}"'.format(self.template_fullpath, self.name))

    def _textfsm_init(self):
        try:
            import textfsm
        except ImportError as e:
            self.log('error', 'You\'ll need to install textfsm Python module to use textfsm style parsing.')
            raise
        try:
            self._textfsm = textfsm.TextFSM(open(self.template_fullpath))
        except textfsm.TextFSMTemplateError as e:
            self.log('error', 'TextFSMTemplateError "{}" while parsing TextFSM template "{}" in Data "{}"'.format(e, self.template_fullpath, self.name))
            raise
        if self.typeoverride:
            # to signal to dispach method it needts to set type_instance
            self.table = True

    def parse(self, output):
        this_tfsm = deepcopy(self._textfsm)
        this_tfsm.ParseText(output)
        return self._textfsm_to_dict(this_tfsm)

    def _textfsm_to_dict(self, tfsm):
        results = {}
        self.log('info', 'TextFSM result: {}'.format(repr(tfsm._result)))
        # Convert TextFSM object to list of dictionaries (by Kirk Byers)
        temp_dict = None
        for row in tfsm._result:
            temp_dict = {}
            for index, element in enumerate(row):
                header = tfsm.header[index].lower()
                if self.table and self.typeinstance and header == self.typeinstance.lower():
                    results[str(element)] = temp_dict
                elif self.types and header not in self.types:
                    # this is a field we do not want
                    continue
                else:
                    temp_dict[header] = element
        if not self.table and temp_dict:
            # if TypeInstance not in configuration, assume only one record will
            # be returned -> place it under key '0'
            results['0'] = temp_dict
        if self.typeoverride:
            # if user set TypeOverride in the config, we can only support one
            # result from textfsm.
            # We actually change type into type_instance and set type to value
            # from config.
            results = {}
            for typ_inst, val in temp_dict.items():
                results[typ_inst] = {self.typeoverride: val}
        self.log('info', repr(results))
        return results
