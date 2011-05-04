# -*- coding: utf-8 -*-
"""
    vt102.screen
    ~~~~~~~~~~~~

    A screen is an in memory buffer of strings that represents the screen
    display of the terminal. It can be instantiated on it's own and given
    explicit commands, or it can be attached to a stream and will respond
    to events.
"""

from __future__ import print_function, absolute_import

from array import array
from collections import namedtuple

from .graphics import text, colors
from . import modes as mo, control as ctrl


#: A container for screen's scroll margins.
margins = namedtuple("margins", "top bottom")


class screen(object):
    """
    .. attribute:: display

       A list of :class:`array.array` objects, holding screen buffer.

    .. attribute:: attributes

       A matrix of character attributes, is allways the same size as
       :attr:`display`.

    .. attribute:: default_attributes

       Default colors and styling. The value of this attribute should
       always be immutable, since shallow copies are made when resizing /
       applying / deleting / printing.

       Attributes are represented by a three-tuple that consists of the
       following:

       1. A tuple of all the text attributes: **bold**, `italic`, etc
       2. Foreground color as a string, see :attr:`vt102.graphics.colors`
       3. Background color as a string, see :attr:`vt102.graphics.colors`

    .. attribute:: margins

       Top and bottom margins, defining the scrolling region; the actual
       values are top and bottom line.

    .. attribute:: buffer

       A list of string which should be sent to the host, for example
       :data:`vt102.escape.DA` replies.
    """
    default_attributes = (), "default", "default"

    def __init__(self, lines, columns):
        # From ``man terminfo`` -- "... hardware tabs are initially set every
        # `n` spaces when the terminal is powered up. Since we aim to support
        # VT102 / VT220 and linux -- we use n = 8.
        self.tabstops = set(xrange(7, columns, 8))
        self.cursor_save_stack = []
        self.lines, self.columns = lines, columns
        self.reset()

    def __repr__(self):
        return repr([l.tounicode() for l in self.display])

    @property
    def cursor(self):
        """Returns cursor's column and line numbers."""
        return self.x, self.y

    @property
    def size(self):
        """Returns screen size -- ``(lines, columns)``."""
        return self.lines, self.columns

    def attach(self, events):
        """Attaches a screen to an object, which processes commands
        and dispatches events.
        """
        handlers = [
            ("reset", self.reset),
            ("print", self.print),
            ("backspace", self.backspace),
            ("tab", self.tab),
            ("linefeed", self.linefeed),
            ("carriage-return", self.carriage_return),
            ("index", self.index),
            ("reverse-index", self.reverse_index),
            ("save-cursor", self.save_cursor),
            ("restore-cursor", self.restore_cursor),
            ("cursor-up", self.cursor_up),
            ("cursor-down", self.cursor_down),
            ("cursor-forward", self.cursor_forward),
            ("cursor-back", self.cursor_back),
            ("cursor-down1", self.cursor_down1),
            ("cursor-up1", self.cursor_up1),
            ("cursor-position", self.cursor_position),
            ("cursor-to-column", self.cursor_to_column),
            ("cursor-to-line", self.cursor_to_line),
            ("erase-in-line", self.erase_in_line),
            ("erase-in-display", self.erase_in_display),
            ("insert-lines", self.insert_line),
            ("delete-lines", self.delete_line),
            ("insert-characters", self.insert_characters),
            ("delete-characters", self.delete_characters),
            ("erase-characters", self.erase_characters),
            ("select-graphic-rendition", self.select_graphic_rendition),
            ("bell", self.bell),
            ("set-tab-stop", self.set_tab_stop),
            ("clear-tab-stop", self.clear_tab_stop),
            ("set-margins", self.set_margins),
            ("set-mode", self.set_mode),
            ("reset-mode", self.reset_mode),
            ("alignment-display", self.alignment_display),
            ("answer", self.answer)

            # Not implemented
            # ...............
            # ("status-report", ...)

            # Not supported
            # .............
            # ("shift-in", ...)
            # ("shift-out")
        ]

        for event, handler in handlers:
            events.connect(event, handler)

    def reset(self):
        """Resets the terminal to its initial state.

        * Scroll margins are reset to screen boundaries.
        * Cursor is moved to home location -- ``(0, 0)`` and its
          attributes are set to defaults (:attr:`default_attributes`)
        * Screen buffer is emptied.
        """
        size = self.size

        self.display = []
        self.attributes = []
        self.buffer = []
        self.mode = set([mo.DECAWM, mo.DECTCEM, mo.LNM])
        self.margins = 0, self.lines - 1
        self.cursor_attributes = self.default_attributes
        self.lines, self.columns = 0, 0

        self.resize(*size)
        self.home()

    def resize(self, lines, columns):
        """Resize the screen.

        If the requested screen size has more lines than the existing
        screen, lines will be added at the bottom. If the requested
        size has less lines than the existing screen lines will be
        clipped at the top of the screen.

        Similarly if the existing screen has less columns than the
        requested size, columns will be added at the right, and it
        has more, columns will be clipped at the right.
        """
        assert lines and columns

        # First resize the lines ...
        if self.lines < lines:
            # If the current display size is shorter than the requested
            # screen size, then add lines to the bottom. Note that the
            # old column size is used here so these new lines will get
            # expanded / contracted as necessary by the column resize
            # when it happens next.
            initial = u" " * self.columns

            for _ in xrange(lines - self.lines):
                self.display.append(array("u", initial))
                self.attributes.append(
                    [self.default_attributes] * self.columns
                )
        elif self.lines > lines:
            # If the current display size is taller than the requested
            # display, then take lines off the top.
            self.display = self.display[self.lines - lines: ]
            self.attributes = self.attributes[self.lines - lines:]

        # ... next, of course, resize the columns.
        if self.columns < columns:
            # If the current display size is thinner than the requested
            # size, expand each line to be the new size.
            initial = u" " * (columns - self.columns)

            self.display = [
                line + array("u", initial) for line in self.display
            ]
            self.attributes = [
                line + [self.default_attributes] * (columns - self.columns)
                for line in self.attributes
            ]
        elif self.columns > columns:
            # If the current display size is fatter than the requested size,
            # then trim each line from the right to be the new size.
            self.display = [
                line[:columns - self.columns] for line in self.display
            ]
            self.attributes = [
                line[:columns - self.columns] for line in self.attributes
            ]

        self.lines, self.columns = lines, columns

    def set_margins(self, top=None, bottom=None):
        """Selects top and bottom margins, defining the scrolling region.

        Margins determine which screen lines move during scrolling (see
        :meth:`index` and :meth:`reversed_index`). Characters added
        outside the scrolling region do not cause the screen to scroll.
        """
        if top is None or bottom is None:
            return

        # The minimum size of the scrolling region is two lines.
        if bottom - top >= 2:
            self.margins = margins(top, bottom)
            # The cursor moves to the home position when the top and
            # bottom margins of the scrolling region (DECSTBM) changes.
            self.home()

    def set_mode(self, *modes):
        """Sets (enables) a given list of modes.

        :param modes: modes to set, where each mode is a constant from
                     :mod:`vt102.modes`.
        """
        if mo.DECCOLM in modes:
            self.resize(self.lines, 132)

        self.mode.update(modes)

    def reset_mode(self, *modes):
        """Resets (disables) a given list of modes.

        :param modes: modes to reset -- hopefully, each mode is a constant
                      from :mod:`vt102.modes`.
        """
        try:
            self.mode.difference_update(modes)
        except KeyError:
            pass
        finally:
            if mo.DECCOLM in modes:
                self.resize(self.lines, 80)

    def print(self, char):
        """Print a character at the current cursor position and advance
        the cursor if :data:`vt102.modes.DECAWM` is set.
        """
        # If this was the last column in a line and auto wrap mode is
        # enabled, move the cursor to the next line. Otherwise replace
        # characters already displayed with newly entered.
        if self.x == self.columns:
            if mo.DECAWM in self.mode:
                self.linefeed()
            else:
                self.x -= 1

        try:
            self.display[self.y][self.x] = char
            self.attributes[self.y][self.x] = self.cursor_attributes
        except IndexError as e:
            if __debug__: print(e, self.x, self.y, char)

        # .. note:: We can't use :meth:`_cursor_forward()`, because that
        #           way, we'll never know when to linefeed.
        self.x += 1

    def carriage_return(self):
        """Move the cursor to the beginning of the current line."""
        self.cursor_to_column(0)

    def index(self):
        """Move the cursor down one line in the same column. If the
        cursor is at the last line, create a new line at the bottom.
        """
        top, bottom = self.margins

        if self.y == bottom:
            self.display.pop(top)
            self.display.insert(bottom, array("u", u" " * self.columns))
        else:
            self.cursor_down()

    def reverse_index(self):
        """Move the cursor up one line in the same column. If the cursor
        is at the first line, create a new line at the top.
        """
        top, bottom = self.margins

        if self.y == top:
            self.display.pop(bottom)
            self.display.insert(top, array("u", u" " * self.columns))
        else:
            self.cursor_up()

    def linefeed(self):
        """Performs an index and, if :data:`vt102.modes.LNM` is set, a
        carriage return."""
        self.index()

        if mo.LNM in self.mode:
            self.carriage_return()

    def tab(self):
        """Move to the next tab space, or the end of the screen if there
        aren't anymore left.
        """
        for stop in sorted(self.tabstops):
            if self.x < stop:
                column = stop
                break
        else:
            column = self.columns - 1

        self.cursor_to_column(column)

    def backspace(self):
        """Move cursor to the left one or keep it in it's position if
        it's at the beginning of the line already.
        """
        self.cursor_back()

    def save_cursor(self):
        """Push the current cursor position onto the stack."""
        self.cursor_save_stack.append(self.cursor)

    def restore_cursor(self):
        """Set the current cursor position to whatever cursor is on top
        of the stack.
        """
        if self.cursor_save_stack:
            # .. todo:: use _cursor_position()
            self.x, self.y = self.cursor_save_stack.pop()
        else:
            # From VT220 Programming Reference Manual: "If none of the
            # characteristics were saved, the cursor moves to home position;
            # origin mode is reset; no character attributes are assigned;
            # and the default character set mapping is established."
            self.home()

    def insert_line(self, count=1):
        """Inserts the indicated # of lines at line with cursor. Lines
        displayed **at** and below the cursor move down. Lines moved
        past the bottom margin are lost.

        .. todo:: reset attributes of the newly inserted lines?

        :param count: number of lines to delete.
        """
        top, bottom = self.margins

        # If cursor is outside scrolling margins it -- do nothin'.
        if top <= self.y <= bottom:
            initial = u" " * self.columns

            for line in xrange(self.y, min(bottom + 1, self.y + count)):
                self.display.pop(bottom)
                self.display.insert(line, array("u", initial))

            self.cursor_to_column(0)

    def delete_line(self, count=1):
        """Deletes the indicated # of lines, starting at line with
        cursor. As lines are deleted, lines displayed below cursor
        move up. Lines added to bottom of screen have spaces with same
        character attributes as last line moved up.

        .. todo:: reset attributes of the deleted lines?

        :param count: number of lines to delete.
        """
        top, bottom = self.margins

        # If cursor is outside scrolling margins it -- do nothin'.
        if top <= self.y <= bottom:
            #                v -- +1 to include the bottom margin.
            for _ in xrange(min(bottom - self.y + 1, count)):
                self.display.pop(self.y)
                self.display.insert(bottom, array("u", u" " * self.columns))

            self.cursor_to_column(0)

    def insert_characters(self, count=0):
        """Inserts the indicated # of blank characters at the cursor
        position. The cursor does not move and remains at the beginning
        of the inserted blank characters.

        :param count: number of characters to delete.
        """
        # From VT220 Programming Reference Manual: "A parameter of 0
        # or 1 inserts one blank character."
        count = count or 1

        for _ in xrange(min(self.columns - self.y, count)):
            self.display[self.y].insert(self.x, u" ")
            self.display[self.y].pop(-1)

            self.attributes[self.y][self.x] = self.default_attributes

    def delete_characters(self, count=1):
        """Deletes the indicated # of characters, starting with the
        character at cursor position. When a character is deleted, all
        characters to the right of cursor move left. Character attributes
        move with the characters.

        :param count: number of characters to delete.
        """
        for _ in xrange(min(self.columns - self.x, count)):
            self.display[self.y].pop(self.x)
            self.display[self.y].append(u" ")

            self.attributes[self.y].pop(self.x)
            self.attributes[self.y].append(self.default_attributes)

    def erase_characters(self, count=0):
        """Erases the indicated # of characters, starting with the
        character at cursor position.  Character attributes are set
        to normal. The cursor remains in the same position.

        :param count: number of characters to erase.
        """
        count = count or 1

        for column in xrange(self.x, min(self.x + count,
                                         self.columns)):
            self.display[self.y][column] = u" "
            self.attributes[self.y][column] = self.default_attributes

    def erase_in_line(self, type_of=0):
        """Erases a line in a specific way, depending on the ``type_of``
        value:

        * ``0`` -- Erases from cursor to end of line, including cursor
          position.
        * ``1`` -- Erases from beginning of line to cursor, including cursor
          position.
        * ``2`` -- Erases complete line.
        """
        line = self.display[self.y]
        attrs = self.attributes[self.y]

        if type_of == 0:
            # a) erase from the cursor to the end of line, including
            # the cursor,
            count = self.columns - self.x
            self.display[self.y] = line[:self.x] + array("u", u" " * count)
            self.attributes[self.y] = attrs[:self.x] + \
                                      [self.default_attributes] * count
        elif type_of == 1:
            # b) erase from the beginning of the line to the cursor,
            # including it,
            count = self.x + 1
            self.display[self.y] = array("u", u" " * count) + line[count:]
            self.attributes[self.y] = [self.default_attributes] * count + \
                                      attrs[count:]
        elif type_of == 2:
            # c) erase the entire line.
            self.display[self.y] = array("u", u" " * self.columns)
            self.attributes[self.y] = [self.default_attributes] * self.columns

    def erase_in_display(self, type_of=0):
        """Erases display in a specific way, depending on the ``type_of``
        value:

        * ``0`` -- Erases from cursor to end of screen, including cursor
          position.
        * ``1`` -- Erases from beginning of screen to cursor, including
          cursor position.
        * ``2`` -- Erases complete display. All lines are erased and
          changed to single-width. Cursor does not move.
        """
        initial = u" " * self.columns
        interval = (
            # a) erase from cursor to the end of the display, including
            # the cursor,
            xrange(self.y, self.lines),
            # b) erase from the beginning of the display to the cursor,
            # including it.
            xrange(0, self.y + 1),
            # c) erase the whole display.
            xrange(0, self.lines)
        )[type_of]

        for line in interval:
            self.display[line] = array("u", initial)
            self.attributes[line] = [self.default_attributes] * self.columns

    def set_tab_stop(self):
        """Sest a horizontal tab stop at cursor position."""
        self.tabstops.add(self.x)

    def clear_tab_stop(self, type_of=None):
        """Clears a horizontal tab stop in a specific way, depending
        on the ``type_of`` value:

        * ``0`` or nothing -- Clears a horizontal tab stop at cursor
          position.
        * ``3`` -- Clears all horizontal tab stops.
        """
        if not type_of:
            # Clears a horizontal tab stop at cursor position, if it's
            # present, or silently fails if otherwise.
            self.tabstops.discard(self.x)
        elif type_of == 3:
            self.tabstops = set([])  # Clears all horizontal tab stops.

    def cursor_up(self, count=1):
        """Moves cursor up the indicated # of lines in same column.
        Cursor stops at top margin.

        :param count: number of lines to skip.
        """
        self.cursor_to_line(self.y - count, within_margins=True)

    def cursor_up1(self, count=1):
        """Moves cursor up the indicated # of lines to column 1. Cursor
        stops at bottom margin.

        :param count: number of lines to skip.
        """
        self.cursor_up(count)
        self.carriage_return()

    def cursor_down(self, count=1):
        """Moves cursor down the indicated # of lines in same column.
        Cursor stops at bottom margin.

        :param count: number of lines to skip.
        """
        self.cursor_to_line(self.y + count, within_margins=True)

    def cursor_down1(self, count=1):
        """Moves cursor down the indicated # of lines to column 1.
        Cursor stops at bottom margin.

        :param count: number of lines to skip.
        """
        self.cursor_down(count)
        self.carriage_return()

    def cursor_back(self, count=1):
        """Moves cursor left the indicated # of columns. Cursor stops
        at left margin.

        :param count: number of columns to skip.
        """
        self.cursor_to_column(self.x - count)

    def cursor_forward(self, count=1):
        """Moves cursor right the indicated # of columns. Cursor stops
        at right margin.

        :param count: number of columns to skip.
        """
        self.cursor_to_column(self.x + count)

    def cursor_position(self, line=0, column=0):
        """Set the cursor to a specific `line` and `column`.

        Cursor is allowed to move out of the scrolling region only when
        :data:`vt102.modes.DECOM` is reset, otherwise -- the position
        doesn't change.

        .. note::

           Obnoxiously, line and column are 1-based, instead of zero
           based, so we need to compensate. Confoundingly, inputs of 0
           are still acceptable, and should move to the beginning of
           the line or column as if they were 1 -- *sigh*.
        """
        line, column  = (line or 1) - 1, (column or 1) - 1
        if (mo.DECOM in self.mode and
            self.margins and
            not self.margins.top <= line <= self.margins.bottom):
            return
        else:
            self.cursor_to_line(line)
            self.cursor_to_column(column)

    def cursor_to_column(self, column=0):
        """Moves cursor to a specific column in the current line.

        :param column: column number to move the cursor to (starts
                       with ``0``).
        """

        self.x = min(max(0, column), self.columns - 1)

    def cursor_to_line(self, line=0, within_margins=False):
        """Moves cursor to a specific line in the current column.

        .. note::

           ``within_margins`` is assumed to be allways ``True`` when
           :data:`vt102.modes.DECOM` is set.

        :param line: line number to move the cursor to (starts with ``0``).
        :param within_margins: when ``True``, cursor is bounded by top
                               and bottom margins, otherwise :attr:`lines`
                               and ``0`` is used.
        """
        if (within_margins or mo.DECOM in self.mode):
            top, bottom = self.margins
        else:
            top, bottom = 0, self.lines - 1

        self.y = min(max(top, line), bottom)

    def home(self):
        """Moves cursor to `home` position.

        When :data:`vt102.modes.DECOM` is reset, `home` position is at
        the left upper corner of the screen, otherwise it's at top margin
        of the user-defined scrolling region.
        """
        if mo.DECOM in self.mode:
            self.cursor_position(0, self.margins.top)
        else:
            self.cursor_position(0, 0)

    def bell(self, *args):
        """Bell stub -- the actual implementation should probably be
        provided by the end-user.
        """

    def alignment_display(self):
        """Fills screen with uppercase E's for screen focus and alignment."""
        for line in xrange(self.lines):
            for column in xrange(self.columns):
                self.display[line][column] = u"E"

    def answer(self, *args):
        """Reports device attributes.

        There are two DA exchanges (dialogues) between the host computer
        and the terminal:

        * In the primary DA exchange, the host asks for the terminal's
          service class code and the basic attributes.
        * In the secondary DA exchange, the host asks for the terminal's
          identification code, firmware version level, and an account
          of the hardware options installed.

        .. note::

           ``vt102`` only implements primary DA exchange, since secondary
           DA exchange doesn't make much sense in the case of a digital
           terminal.
        """
        if len(args) == 1:
            attrs = [
                u"62",  # I'm a service class 2 terminal
                u"1",   # with 132 columns
                u"6",   # and selective erase.
            ]
            self.buffer.append(u"%s?%sc" % (unichr(ctrl.CSI), u";".join(attrs)))

    # The following methods weren't tested properly yet.
    # ..................................................

    def remove_text_attr(self, attr):
        current = set(self.cursor_attributes[0])
        if attr in current:
            current.remove(attr)
        return tuple(current) + self.cursor_attributes[1:]

    def add_text_attr(self, attr):
        current = set(self.cursor_attributes[0])
        current.add(attr)
        attrs = self.cursor_attributes[1:]
        return (tuple(current), attrs[0], attrs[1])

    def text_attr(self, attr):
        """
        Given a text attribute, set the current cursor appropriately.
        """
        attr = text[attr]
        if attr == "reset":
            self.cursor_attributes = self.default_attributes
        elif attr == "underline-off":
            self.cursor_attributes = self.remove_text_attr("underline")
        elif attr == "blink-off":
            self.cursor_attributes = self.remove_text_attr("blink")
        elif attr == "reverse-off":
            self.cursor_attributes = self.remove_text_attr("reverse")
        else:
            self.cursor_attributes = self.add_text_attr(attr)

    def color_attr(self, ground, attr):
        """
        Given a color attribute, set the current cursor appropriately.
        """
        attr = colors[ground][attr]
        attrs = self.cursor_attributes
        if ground == "foreground":
            self.cursor_attributes = (attrs[0], attr, attrs[2])
        elif ground == "background":
            self.cursor_attributes = (attrs[0], attrs[1], attr)

    def set_attr(self, attr):
        """
        Given some text attribute, set the current cursor attributes
        appropriately.
        """
        if attr in text:
            self.text_attr(attr)
        elif attr in colors["foreground"]:
            self.color_attr("foreground", attr)
        elif attr in colors["background"]:
            self.color_attr("background", attr)

    def select_graphic_rendition(self, *attrs):
        """
        Set the current text attribute.
        """

        if not attrs:
            # No arguments means that we're really trying to do a reset.
            attrs = [0]

        for attr in attrs:
            self.set_attr(attr)

