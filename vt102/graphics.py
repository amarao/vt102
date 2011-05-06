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
    2: "dim" ,
    4: "underline",
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
        39: "default",
        # This is technically "default with underscore", but I don't
        # understand the utility of mixing the text styling with the
        # colors. Instead I'm going to just leave it as "default" until
        # I see something buggy or someone complains.
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

# Compatibility aliases.
colors, text = COLORS, TEXT
