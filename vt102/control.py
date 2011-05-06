# -*- coding: utf-8 -*-
"""
    vt102.control
    ~~~~~~~~~~~~~

    This module defines simple control sequences, recognized by
    :class:`vt102.streams.Stream`, although named `vt102`, the set
    of codes here is for ``TERM=linux`` which is a superset of
    `vt102`.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

"""Null: Does nothing."""
NUL = u"\x00"

"""Bell: Beeps."""
BEL = u"\x07"

"""Backspace: Backspaces one column, but not past the begining of the line."""
BS = u"\x08"

"""Horizontal tab: Moves cursor to the next tab stop, or to the end of
the line if there is no earlier tab stop."""
HT = u"\x09"

"""Linefeed, vertical tab, form feed: all give a line feed, and if LF/NL
(new line mode) is set also a carriage return."""
LF, VT, FF = u"\n", u"\x0b", u"\x0c"

"""Carriage return: Moves cursor to left margin on current line."""
CR = u"\r"

"""Shift out: Activates G1 character set."""
SO = u"\x0e"

"""Shift in: Activates G0 character set."""
SI = u"\x0f"

"""Cancel, substitute: interrupt escape sequences. If received during
an escape or control sequence, cancels the sequence and displays
substitution character."""
CAN, SUB = u"\x18", u"\x1a"

"""Escape: Starts an escape sequence."""
ESC = u"\x1b"

"""Delete: is ingored."""
DEL = u"\x7f"

"""Control sequence introducer: is equavalent for ``ESC [``."""
CSI = u"\x9b"
