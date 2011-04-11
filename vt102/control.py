# -*- coding: utf-8 -*-
"""
    vt102.control
    ~~~~~~~~~~~~~

    A container for control sequences, recognized by :class:`vt102.stream`,
    although named `vt102`, the set of codes here is for ``TERM=linux``,
    which is a superset of `vt102`.

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow.

    :copyright: (c) 2011 by Sam Gibson, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

"""Bell: Beeps."""
BEL = 0x07

"""Backspace: Backspaces one column, but not past the begining of the line."""
BS = 0x08

"""Horizontal tab: Moves cursor to the next tab stop, or to the end of
the line if there is no earlier tab stop."""
HT = 0x09

"""Linefeed, vertical tab, form feed: all give a line feed, and if LF/NL
(new line mode) is set also a carriage return."""
LF, VT, FF = 0x0A, 0x0B, 0x0C

"""Carriage return: Moves cursor to left margin on current line."""
CR = 0x0D

"""Shift out: Activates G1 character set."""
SO = 0x0E

"""Shift in: Activates G0 character set."""
SI = 0x0F

"""Cancel, substitute: interrupt escape sequences. If received during
an escape or control sequence, cancels the sequence and displays
substitution character."""
CAN, SUB = 0x18, 0x1A

"""Escape: Starts an escape sequence."""
ESC = 0x1B

"""Delete: is ingored."""
DEL = 0x7F

"""Control sequence introducer: is equavalent for ``ESC [``."""
CSI = 0x9B
