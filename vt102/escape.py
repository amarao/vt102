# -*- coding: utf-8 -*-
"""
    vt102.escape
    ~~~~~~~~~~~~

    This module defines bot CSI and non-CSI escape sequences, recognized
    by :class:`vt102.streams.Stream` and subclasses.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

#: *Reset*.
RIS = u"c"

#: *Index*: Move cursor down one line in same column. If the cursor is
#: at the bottom margin, the screen performs a scroll-up.
IND = u"D"

#: *Next line*: Same as :data:`vt102.control.LF`.
NEL = u"E"

#: Tabulation set: Set a horizontal tab stop at cursor position.
HTS = u"H"

#: *Reverse index*: Move cursor up one line in same column. If the
#: cursor is at the top margin, the screen performs a scroll-down.
RI = u"M"

#: Save cursor: Save cursor position, character attribute (graphic
#: rendition), character set, and origin mode selection (see
#: :data:`DECRC`).
DECSC = u"7"

#: *Restore cursor*: Restore previously saved cursor position, character
#: attribute (graphic rendition), character set, and origin mode
#: selection. If none were saved, move cursor to home position.
DECRC = u"8"


# "Sharp" escape sequences.
# -------------------------

#: *Alignment display*: Fill screen with uppercase E's for testing
#: screen focus and alignment.
DECALN = u"8"


# ECMA-48 CSI sequences.
# ---------------------

#: *Insert character*: Insert the indicated # of blank characters.
ICH = u"@"

#: *Cursor up*: Move cursor up the indicated # of lines in same column.
#: Cursor stops at top margin.
CUU = u"A"

#: *Cursor down*: Move cursor down the indicated # of lines in same
#: column. Cursor stops at bottom margin.
CUD = u"B"

#: *Cursor forward*: Move cursor right the indicated # of columns.
#: Cursor stops at right margin.
CUF = u"C"

#: *Cursor back*: Move cursor left the indicated # of columns. Cursor
#: stops at left margin.
CUB = u"D"

#: *Cursor next line*: Move cursor down the indicated # of lines to
#: column 1.
CNL = u"E"

#: *Cursor previous line*: Move cursor up the indicated # of lines to
#: column 1.
CPL = u"F"

#: *Cursor horizontal align*: Move cursor to the indicated column in
#: current line.
CHA = u"G"

#: *Cursor position*: Move cursor to the indicated line, column (origin
#: at ``1, 1``).
CUP = u"H"

#: *Erase data* (default: from cursor to end of line).
ED = u"J"

#: *Erase in line* (default: from cursor to end of line).
EL = u"K"

#: *Insert line*: Insert the indicated # of blank lines, starting from
#: the current line. Lines displayed below cursor move down. Lines moved
#: past the bottom margin are lost.
IL = u"L"

#: *Delete line*: Delete the indicated # of lines, starting from the
#: current line. As lines are deleted, lines displayed below cursor
#: move up. Lines added to bottom of screen have spaces with same
#: character attributes as last line move up.
DL = u"M"

#: *Delete character*: Delete the indicated # of characters on the
#: current line. When character is deleted, all characters to the right
#: of cursor move left.
DCH = u"P"

#: *Erase character*: Erase the indicated # of characters on the
#: current line.
ECH = u"X"

#: *Horizontal position relative*: Same as :data:`CUF`.
HPR = u"a"

#: *Vertical position adjust*: Move cursor to the indicated line,
#: current column.
VPA = u"d"

#: *Vertical position relative*: Same as :data:`CUD`.
VPR = u"e"

#: *Horizontal / Vertical position*: Same as :data:`CUP`.
HVP = u"f"

#: *Tabulation clear*: Clears a horizontal tab stop at cursor position.
TBC = u"g"

#: *Set mode*.
SM = u"h"

#: *Reset mode*.
RM = u"l"

#: *Select graphics rendition*: The terminal can display the following
#: character attributes that change the character display without
#: changing the character (see :mod:`vt102.graphics`).
SGR = u"m"

#: *Select top and bottom margins*: Selects margins, defining the
#: scrolling region; parameters are top and bottom line. If called
#: without any arguments, whole screen is used.
DECSTBM = u"r"

#: *Horizontal position adjust*: Same as :data:`CHA`.
HPA = u"'"
