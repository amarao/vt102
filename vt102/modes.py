# -*- coding: utf-8 -*-
"""
    vt102.modes
    ~~~~~~~~~~~

    This module defines terminal mode switches, used by
    :class:`vt102.screens.Screen`.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

"""Line Feed/New Line Mode: when enabled, causes a received
:data:`escape.LF`, :data:`escape.FF`, or :data:`escape.VT` to move the
cursor to the first column of the next line."""
LNM = 20

"""Insert/Replace Mode: when enabled, new display characters move old
display characters to the right. Characters moved past the right margin
are lost. Otherwise, new display characters replace old display
characters at the cursor position. """
IRM = 4


# Private modes.
# ..............

"""Text Cursor Enable Mode: determines if the text cursor is visible."""
DECTCEM = 25

"""Cursor Key Mode: when enabled cursor keys send application control
functions, otherwise they generate ANSI cursor control sequences."""
DECCKM = 1

"""Origin Mode: allows cursor addressing relative to a user-defined
origin. This mode resets when the terminal is powered up or reset. It
does not affect the erase in display (ED) function."""
DECOM = 6

"""Auto Wrap Mode: selects where received graphic characters appear
when the cursor is at the right margin."""
DECAWM = 7

"""Column Mode: selects the number of columns per line (80 or 132) on
the screen."""
DECCOLM = 3
