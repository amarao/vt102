# -*- coding: utf-8 -*-
"""
    vt102.debug
    ~~~~~~~~~~~

    A container for various debugging helpers.

    :copyright: (c) 2011 by Sam Gibson, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

from vt102 import stream

class explainer(stream):
    def dispatch(self, event, *args):
        print "%s %r" % (event, args)
