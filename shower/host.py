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

import time
from netmiko import ConnectHandler
from netmiko import platforms as netmiko_platforms
from netmiko import NetMikoTimeoutException
from .base import ShowerBase
from .exceptions import ShowerConfigException


class Host(ShowerBase):
    def __init__(self, conf, global_conf={}):
        super(Host, self).__init__()
        self.name = str(conf.values[0])
        self.address = None
        self.type = None
        self.collect = []
        self.username = None
        self.password = None
        #self.ssh_key TODO
        self.connection = None
        self.connected = False
        self.debug = False
        self.timeout = 2
        self.global_interval = 10
        self.interval = self.global_interval
        self._skipped_seconds = None
        self._from_conf(global_conf, conf)
        self._validate()

    def _from_conf(self, global_conf, conf):
        for key, value in global_conf.items():
            setattr(self, key, value)
        for node in conf.children:
            key = node.key.lower()
            if key in ['type', 'address', 'username', 'password']:
                setattr(self, key, str(node.values[0]))
            elif key in ['collect']:
                setattr(self, key, node.values)
            elif key in ['verbose', 'debug']:
                setattr(self, key, bool(node.values[0]))
            elif key in ['interval', 'timeout']:
                setattr(self, key, int(node.values[0]))
            # TODO ssh_key

    def _validate(self):
        if not self.name:
            raise ShowerConfigException('Unnamed Host config section')
        if self.address is None:
            self.address = self.name
        # TODO ssh_key checking/loading
        if self.type not in netmiko_platforms:
            raise ShowerConfigException('Device type "{}" not supported by netmiko [{}]'.format(self.type, self.name))
        if self.interval < 1 or self.interval < self.global_interval or self.interval % self.global_interval:
            raise ShowerConfigException('Device interval "{}" must be a multiple fo globl interval'.format(self.interval))

    def connect(self):
        self.log('info', 'connecting'.format(self.name))
        start = time.time()
        try:
            self.connection = ConnectHandler(
                device_type = self.type,
                ip = self.address,
                username = self.username,
                password = self.password,
                timeout = self.timeout
            )
            # TODO ssh_key
        except Exception as e:
            took = time.time() - start
            self.log('error', '{} [took:{}s]'.format(e, took))
            self.connected = False
        else:
            took = time.time() - start
            self.log('info', 'connected [took:{}s]'.format(took))
            self.connected = True

    def disconnect(self):
        if self.connected:
            self.connection.disconnect()

    def read_callback(self, worker_id):
        if not self.should_run():
            return
        self.log('info', 'read_callback {}'.format(worker_id))
        start = time.time()
        self.run_commands()
        took = time.time() - start
        self.log('info', 'read_callback {} [took:{}s]'.format(worker_id, took))

    def run_commands(self):
        if not self.connected:
            self.connect()
            # TODO exponential backof
        for data in self.collect:
            if not self.connected:
                break
            output = self.run_command(data.command)
            try:
                results = data.parse(output)
                data.dispach(self, results)
            except Exception as e:
                self.log('error', 'Error parsing command output "{}": {}'.format(data.command, e))

    def run_command(self, command):
        try:
            output = self.connection.send_command(command, max_loops=100)
        except NetMikoTimeoutException as e:
            self.connected = False
            self.log('error', str(e))
            return None
        except Exception as e:
            # TODO detect more kinds of exceptions and handle accordingly
            self.connected = False
            self.log('error', str(e))
            return None
        else:
            if self.debug:
                self.log('info', 'cmd:"{}" len:"{}" output:"{}"'.format(command, len(output), output))
            return output

    def should_run(self):
        if self._skipped_seconds is None:
            self._skipped_seconds = 0
            return True
        if self._skipped_seconds + self.global_interval >= self.interval:
            self._skipped_seconds = 0
            return True
        else:
            self._skipped_seconds += self.global_interval
            return False

    def log(self, severity='info', message=''):
        message = '[{}] {}'.format(self.name, message)
        return super(Host, self).log(severity, message)

# vim: tabstop=4 shiftwidth=4 expandtab
