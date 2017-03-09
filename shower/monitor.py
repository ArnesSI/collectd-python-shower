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
import threading
from .base import ShowerBase
from .data import make_data
from .host import Host
from .exceptions import ShowerConfigException


class Shower(ShowerBase):
    def __init__(self):
        super(Shower, self).__init__()
        self.workers = 1
        self.verbose = False
        self.interval = 10
        self.username = None
        self.password = None
        self.datas = {}
        self.hosts = []

    def configure_callback(self, conf):
        host_confs = []
        for node in conf.children:
            key = node.key.lower()
            if key in ['username', 'password']:
                setattr(self, key, str(node.values[0]))
            elif key in ['workers', 'interval']:
                setattr(self, key, int(node.values[0]))
            elif key in ['verbose']:
                setattr(self, key, bool(node.values[0]))
            elif key == 'data':
                data = make_data(node)
                self.datas[data.name] = data
            elif key == 'host':
                host_confs.append(node)
        global_conf = {
            'verbose': self.verbose,
            'global_interval': self.interval,
            'username': self.username,
            'password': self.password
        }
        for host_conf in host_confs:
            self.hosts.append(Host(host_conf, global_conf=global_conf))
        self._validate()
        self.register_read()
        self.log('info', 'configure_callback completed')

    def _validate(self):
        """ replace host.collect strings with apropriate Data instances """
        for host in self.hosts:
            missing = [m for m in host.collect if m not in self.datas.keys()]
            if missing:
                raise ShowerConfigException('The following collect values on host {} are not defined {}'.format(host.host, missing))
            host_datas = [self.datas[c] for c in host.collect]
            host.collect = host_datas

    def register_read(self):
        import collectd
        worker_id = 0
        while worker_id < self.workers:
            ident = collectd.register_read(self.read_callback, self.interval, worker_id, '{}_{}'.format(self.plugin_name, worker_id))
            self.log('info', 'registered read_callback {}'.format(ident))
            worker_id += 1

    def init_callback(self):
        """ establish connection to all hosts """
        self.log('info', 'init_callback')
        start = time.time()
        threads = []
        for host in self.hosts:
            t = threading.Thread(target=host.connect)
            threads.append(t)
            t.start()
        for t in threads:
            t.join(10)
        took = time.time() - start
        self.log('info', 'init_callback finished [took:{}]'.format(took))

    def read_callback(self, worker_id):
        self.log('info', 'read_callback@worker_{}'.format(worker_id))
        start = time.time()
        host_idx = worker_id
        while host_idx < len(self.hosts):
            host = self.hosts[host_idx]
            host.read_callback(worker_id)
            host_idx += self.workers
        took = time.time() - start
        self.log('info', 'read_callback@worker_{} finished [took:{}]'.format(worker_id, took))

    def shutdown_callback(self):
        self.log('info', 'shutdown_callback')
        start = time.time()
        threads = []
        for host in self.hosts:
            t = threading.Thread(target=host.disconnect)
            threads.append(t)
            t.start()
        for t in threads:
            t.join(10)
        took = time.time() - start
        self.log('info', 'shutdown_callback finished [took:{}]'.format(took))

# vim: tabstop=4 shiftwidth=4 expandtab
