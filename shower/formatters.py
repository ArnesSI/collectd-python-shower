# -*- coding: utf-8 -*-
########################################################################
#
# MIT License
#
# Copyright (c) 2017 Matej Vadnjal <matej@arnes.si>, Peter Ciber
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


def multiplier2int(n):
    ''' Example: 10k becomes 10000 '''
    pos_postfixes = [u'k', u'm', u'G', u'T', u'P', u'E', u'Z', u'Y']
    neg_postfixes = [u'M', u'µ', u'n', u'p', u'f', u'a', u'z', u'y']
    num_postfix = n[-1]
    if num_postfix in pos_postfixes:
        num = float(n[:-1])
        num*=10**((pos_postfixes.index(num_postfix)+1)*3)
    elif num_postfix in neg_postfixes:
        num = float(n[:-1])
        num*=10**(-(neg_postfixes.index(num_postfix)+1)*3)
    else:
        num = float(n)
    return num


def to_float(n):
    return float(n)
