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

from .monitor import Shower

try:
    import collectd
except:
    print 'not running from collectd, do something fun here!'
else:
    nt = Shower()

    def configure_callback(*args, **kwargs):
        """
        This method is a workaround - collectd won't call a configure method that
        is not defined in this file
        """
        return nt.configure_callback(*args, **kwargs)

    collectd.register_config(configure_callback)
    collectd.register_init(nt.init_callback)
    collectd.register_shutdown(nt.shutdown_callback)

# vim: tabstop=4 shiftwidth=4 expandtab
