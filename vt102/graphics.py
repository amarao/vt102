# -*- coding: utf-8 -*-
"""
    vt102.graphics
    ~~~~~~~~~~~~~~

    This module defines graphic-related constants, mostly taken from
    ``man console_codes`` and
    http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

SPECIAL = {
    0: "reset",
    7: "reverse",
    27: "-reverse"
}

"""A mapping of ANSI text style codes to style names, example:

>>> text[1]
'bold'
>>> text[9]
'strikethrough'"""
TEXT = {
    1: "bold" ,
    3: "italics",
    4: "underscore",
    9: "strikethrough",
    22: "-bold",
    24: "-underscore",
    25: "-blink",
    29: "-strikethrough"
}


"""A mapping of ANSI foreground color codes to color names, example:

>>> FG[30]
'black'
>>> FG[38]
'default'"""
FG = {
    30: "black",
    31: "red",
    32: "green",
    33: "brown",
    34: "blue",
    35: "magenta",
    36: "cyan",
    37: "white",
    39: "default"  # white.
}

"""A mapping of ANSI background color codes to color names, example:

>>> BG[40]
'black'
>>> BG[48]
'default'"""
BG = {
    40: "black",
    41: "red",
    42: "green",
    43: "brown",
    44: "blue",
    45: "magenta",
    46: "cyan",
    47: "white",
    49: "default"  # black.
}
