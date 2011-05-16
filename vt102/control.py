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

#: *Null*: Does nothing.
NUL = u"\x00"

#: *Bell*: Beeps.
BEL = u"\x07"

#: *Backspace*: Backspace one column, but not past the begining of the
#: line.
BS = u"\x08"

#: *Horizontal tab*: Move cursor to the next tab stop, or to the end
#: of the line if there is no earlier tab stop.
HT = u"\x09"

#: *Linefeed*: Give a line feed, and, if :data:`vt102.modes.LNM` (new
#: line mode) is set also a carriage return.
LF = u"\n"
#: *Vertical tab*: Same as :data:`LF`.
VT = u"\x0b"
#: *Form feed*: Same as :data:`LF`.
FF = u"\x0c"

#: *Carriage return*: Move cursor to left margin on current line.
CR = u"\r"

#: *Shift out*: Activate G1 character set.
SO = u"\x0e"

#: *Shift in*: Activate G0 character set.
SI = u"\x0f"

#: *Cancel*: Interrupt escape sequence. If received during an escape or
#: control sequence, cancels the sequence and displays substitution
#: character.
CAN = u"\x18"
#: *Substitute*: Same as :data:`CAN`.
SUB = u"\x1a"

#: *Escape*: Starts an escape sequence.
ESC = u"\x1b"

#: *Delete*: Is ingored.
DEL = u"\x7f"

#: *Control sequence introducer*: An equavalent for ``ESC [``.
CSI = u"\x9b"
