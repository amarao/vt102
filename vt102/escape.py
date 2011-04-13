# -*- coding: utf-8 -*-
"""
    vt102.escape
    ~~~~~~~~~~~~

    A container for escape sequences, recognized by :class:`vt102.stream`

    :copyright: (c) 2011 by Sam Gibson, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

# ESC- but not CSI-sequences (incomplete -- missing at least ``DECALN`,
# ``DECPNM``, ``DECPAM``, ``OSC``).

"""Reset."""
RIS = 0x63

"""Index: Move cursor down one line in same column. If the cursor is
at the bottom margin, the screen performs a scroll-up."""
IND = 0x44

"""Next line: Same as :data:`control.LF`."""
NEL = 0x45

"""Tabulation set: Set a horizontal tab stop at cursor position."""
HTS = 0x48

"""Reverse index: Move cursor up one line in same column. If the cursor
is at the top margin, the screen performs a scroll-down."""
RI = 0x4D

"""Save cursor: Save cursor position, character attribute (graphic
rendition), character set, and origin mode selection (see
:data:`DECRC`)."""
DECSC = 0x37

"""Restore cursor: Restore previously saved cursor position, character
attribute (graphic rendition), character set, and origin mode selection.
If none were saved, move cursor to home position."""
DECRC = 0x38


# ECMA-48 CSI seqences.

"""Insert the indicated # of blank characters."""
ICH = 0x40

"""Move cursor up the indicated # of lines in same column. Cursor
stops at top margin.."""
CUU = 0x41

"""Move cursor down the indicated # of lines in same column. Cursor
stops at bottom margin."""
CUD = 0x42

"""Move cursor right the indicated # of columns. Cursor stops at right
margin."""
CUF = 0x43

"""Move cursor left the indicated # of columns. Cursor stops at left
margin."""
CUB = 0x44

"""Move cursor down the indicated # of lines to column 1."""
CNL = 0x45

"""Move cursor up the indicated # of lines to column 1."""
CPL = 0x46

"""Move cursor to the indicated column in current line."""
CHA = 0x47

"""Move cursor to the indicated line, column  (origin at ``1, 1``)."""
CUP = 0x48

"""Erase data (default: from cursor to end of line)."""
ED = 0x4A

"""Erase in line (default: from cursor to end of line)."""
EL = 0x4B

"""Insert the indicated # of blank lines, starting from the current
line. Lines displayed below cursor move down. Lines moved past the
bottom margin are lost."""
IL = 0x4C

"""Delete the indicated # of lines, starting from the current line. As
lines are deleted, lines displayed below cursor move up. Lines added
to bottom of screen have spaces with same character attributes as last
line move up."""
DL = 0x4D

"""Delete the indicated # of characters on the current line. When a
character is deleted, all characters to the right of cursor move left.
"""
DCH = 0x50

"""Erase the indicated # of characters on the current line."""
ECH = 0x58

"""Same as data:`CUF`."""
HPR = 0x61

"""Answer ``ESC [ ? 6 c``: "I'm a VT102"."""
DA = 0x63

"""Move cursor to the indicated line, current column."""
VPA = 0x64

"""Sake as data:`CUD`."""
VPR = 0x65

"""Same as :data:`CUP`."""
HVP = 0x66

"""Clears a horizontal tab stop at cursor position."""
TBC = 0x67

"""Set mode."""
SM = 0x68

"""Reset mode."""
RM = 0x6c

"""Select graphics rendition. The terminal can display the following
character attributes that change the character display without changing
the character.

* Underline
* Reverse video (character background opposite of the screen background)
* Blink
* Bold (increased intensity)
"""
SGR = 0x6D

"""Status report:

* ``ESC [ 5 n`` -- Device status report (DSR); answer is ``ESC [ 0 n``
  (Terminal OK).

* ``ESC [ 6 n`` -- Cursor position report (CPR); answer is
  ``ESC [ y ; x R``, where x, y is the cursor location.
"""
DSR = 0x6E

"""Selects top and bottom margins, defining the scrolling region;
parameters are top and bottom line. If called without any arguments,
whole screen is used."""
DECSTBM = 0x72

"""Same as :data:`CHA`."""
HPA = 0x60

# .. todo: missing -- ``DECLL``, ``DECSTBM`` and many-many-MANY
#          more ...
