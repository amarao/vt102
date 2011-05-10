# -*- coding: utf-8 -*-
"""
    vt102.graphics
    ~~~~~~~~~~~~~~

    This module defines graphic-related constants.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

"""A mapping of ANSI text style codes to style names, example:

>>> text[1]
'bold'
>>> text[7]
'reverse'"""
TEXT = {
    0: "reset",
    1: "bold" ,
    2: "half-bright" ,
    4: "underscore",
    5: "blink",
    7: "reverse",
    24: "underline-off",
    25: "blink-off",
    27: "reverse-off",
}


"""A mapping of ANSI color codes to color names, example:

>>> colors["foreground"][30]
'black'
>>> colors["background"][42]
'green'"""
COLORS = {
    "foreground": {
        30: "black",
        31: "red",
        32: "green",
        33: "brown",
        34: "blue",
        35: "magenta",
        36: "cyan",
        37: "white",
        39: "default with underscore",
        38: "default",
    },
    "background": {
        40: "black",
        41: "red",
        42: "green",
        43: "brown",
        44: "blue",
        45: "magenta",
        46: "cyan",
        47: "white",
        49: "default",
    }
}
