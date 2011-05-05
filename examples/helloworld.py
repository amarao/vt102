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
    stream = vt102.stream()
    screen = vt102.screen(24, 80)
    screen.attach(stream)
    stream.feed(u"Hello world!")

    for idx, line in enumerate(screen.display, 1):
        print("%2i" % idx, line.tounicode())
