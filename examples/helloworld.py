# -*- coding: utf-8 -*-
"""
    helloworld
    ~~~~~~~~~~

    A minimal working example for :mod:`vt102`.
"""

from __future__ import print_function

import sys
sys.path.append("..")

import vt102


if __name__ == "__main__":
    stream = vt102.Stream()
    screen = vt102.Screen(80, 24)
    screen.attach(stream)
    stream.feed(u"Hello world!")

    for idx, line in enumerate(screen, 1):
        print(u"%2i" % idx, u"".join(c.data for c in line), u"¶")
