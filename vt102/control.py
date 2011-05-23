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
NUL = u"\u0000"

#: *Bell*: Beeps.
BEL = u"\u0007"

#: *Backspace*: Backspace one column, but not past the begining of the
#: line.
BS = u"\u0008"

#: *Horizontal tab*: Move cursor to the next tab stop, or to the end
#: of the line if there is no earlier tab stop.
HT = u"\u0009"

#: *Linefeed*: Give a line feed, and, if :data:`vt102.modes.LNM` (new
#: line mode) is set also a carriage return.
LF = u"\n"
#: *Vertical tab*: Same as :data:`LF`.
VT = u"\u000b"
#: *Form feed*: Same as :data:`LF`.
FF = u"\u000c"

#: *Carriage return*: Move cursor to left margin on current line.
CR = u"\r"

#: *Shift out*: Activate G1 character set.
SO = u"\u000e"

#: *Shift in*: Activate G0 character set.
SI = u"\u000f"

#: *Cancel*: Interrupt escape sequence. If received during an escape or
#: control sequence, cancels the sequence and displays substitution
#: character.
CAN = u"\u0018"
#: *Substitute*: Same as :data:`CAN`.
SUB = u"\u001a"

#: *Escape*: Starts an escape sequence.
ESC = u"\u001b"

#: *Delete*: Is ingored.
DEL = u"\u007f"

#: *Control sequence introducer*: An equavalent for ``ESC [``.
CSI = u"\u009b"
