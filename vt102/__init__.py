# -*- coding: utf-8 -*-
"""
    vt102
    ~~~~~

    `vt102` implements a subset of the vt102 specification (the subset
    that should be most useful for use in software).

    Two classes: :class:`stream`, which parses the command stream and
    dispatches events for commands, and :class:`screen` which, when used
    with a `stream` maintains a buffer of strings representing the screen
    of a terminal.

    :copyright: (c) 2011 by Sam Gibson, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import print_function

from array import array
from collections import defaultdict, namedtuple
from copy import copy

from vt102 import control as ctrl, escape as esc
from vt102.graphics import text, colors, dsg


class stream(object):
    """
    A stream is the state machine that parses a stream of terminal
    characters and dispatches events based on what it sees.

    Quick example:

    >>> import vt102
    >>> class dummy(object):
    ...     def __init__(self):
    ...         self.foo = 0
    ...     def up(self, bar):
    ...         self.foo += bar
    ...
    >>> dummy = dummy()
    >>> stream = vt102.stream()
    >>> stream.connect("cursor-up", dummy.up)
    >>> stream.process("\\x\\00\\1b[5A") # Move the cursor up 5 rows.
    >>> dummy.foo
    5

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow in :attr:`basic`,
            :attr:`escape`, :attr:`sequences`
    """

    #: When ``True``, unknown CSI sequences are being printed, prefixed
    #: with ``"^"``.
    debug = False

    #: Basic characters, which don't require any arguments.
    basic = {
        ctrl.BEL: "bell",
        ctrl.BS: "backspace",
        ctrl.HT: "tab",
        ctrl.LF: "linefeed",
        ctrl.VT: "linefeed",
        ctrl.FF: "linefeed",
        ctrl.CR: "carriage-return",
        ctrl.SO: "shift-out",
        ctrl.SI: "shift-in",
    }

    #: non-CSI escape squences.
    escape = {
        esc.RIS: "reset",
        esc.IND: "linefeed",
        esc.NEL: "newline",
        esc.RI: "reverse-linefeed",
        esc.HTS: "set-tab-stop",
        esc.DECSC: "save-cursor",
        esc.DECRC: "restore-cursor",
    }

    #: CSI escape sequences.
    sequence = {
        esc.ICH: "insert-characters",
        esc.CUU: "cursor-up",
        esc.CUD: "cursor-down",
        esc.CUF: "cursor-forward",
        esc.CUB: "cursor-back",
        esc.CNL: "cursor-down1",
        esc.CPL: "cursor-up1",
        esc.CHA: "cursor-to-column",
        esc.CUP: "cursor-position",
        esc.ED: "erase-in-display",
        esc.EL: "erase-in-line",
        esc.IL: "insert-lines",
        esc.DL: "delete-lines",
        esc.DCH: "delete-characters",
        esc.ECH: "erase-characters",
        esc.DA: "answer",
        esc.HPR: "cursor-forward",
        esc.VPA: "cursor-to-line",
        esc.VPR: "cursor-down",
        esc.HVP: "cursor-position",
        esc.TBC: "clear-tab-stop",
        esc.SM: "set-mode",
        esc.RM: "reset-mode",
        esc.SGR: "select-graphic-rendition",
        esc.DSR: "status-report",
        esc.DECSTBM: "set-margins",
        esc.HPA: "cursor-to-column",
    }

    def __init__(self):
        self.listeners = defaultdict(lambda: [])
        self.reset()

    def reset(self):
        """Resets state to ``"stream"`` and empties parameter attributes."""
        self.state = "stream"
        self.params = []
        self.current_param = ""

    def _escape_sequence(self, char):
        """Handle characters seen when in an escape sequence.

        Most non-VT52 commands start with a left-bracket after the
        escape and then a stream of parameters and a command.
        """
        if char == "[":
            self.state = "escape-lb"
        elif char == "(":
            self.state = "charset-g0"
        elif char == ")":
            self.state = "charset-g1"
        elif ord(char) in self.escape:
            self.state = "stream"
            self.dispatch(self.escape[ord(char)])
        else:
            self.state = "stream"  # Unknown ESC code, silently eat and continue.

    def _end_escape_sequence(self, char):
        """Handle the end of an escape sequence.

        The final character in an escape sequence is the command to
        execute, which corresponds to the event that is dispatched here.
        """
        event = self.sequence.get(ord(char))
        if event:
            self.dispatch(event, *self.params)
        elif self.debug:
            # Unhandled CSI sequences are printed literally.
            self.dispatch("print", u"^")
            self.dispatch("print", u"[")

            for param in u";".join(map(unicode, self.params)):
                self.dispatch("print", param)

            self.dispatch("print", char)

            print("i'm unhandled, boss -- ^[%s"
                  % u";".join(map(unicode, self.params)) + char)

        self.reset()

    def _escape_parameters(self, char):
        """Parse parameters in an escape sequence.

        Parameters are a list of numbers in ASCII (e.g. ``12``, ``4``,
        ``42``, etc) separated by a semicolon (e.g. ``12;4;42``). If
        any of the given param is not a number it's skipped silently.

        .. seealso::

           `VT102 User Guide <http://vt100.net/docs/vt102-ug/>`_
               For details on the formatting of escape parameters.
        """
        if char == "?":
            self.state = "mode"
        elif char == ";":
            self.current_param and self.params.append(int(self.current_param))
            self.current_param = ""
        elif not char.isdigit():
            self.current_param and self.params.append(int(self.current_param))
            # If we're in parameter parsing mode, but we see a non-
            # numeric value, it must be the end of the control sequence.
            self._end_escape_sequence(char)
        else:
            # .. todo: joining strings with `+` is way too slow!
            self.current_param += char

    def _mode(self, char):
        if char in "lh":
            # 'l' or 'h' designates the end of a mode stream. We don't
            # really care about mode streams so anything else seen while
            # in the mode state, is just ignored.
            self.state = "stream"

    def _charset_g0(self, char):
        self.dispatch("charset-g0", char)
        self.state = "stream"

    def _charset_g1(self, char):
        self.dispatch("charset-g1", char)
        self.state = "stream"

    def _stream(self, char):
        """Process a character when in the default ``"stream"`` state."""
        num = ord(char)
        if num in self.basic:
            self.dispatch(self.basic[num])
        elif num == ctrl.ESC:
            self.state = "escape"
        elif num == 0x00:
            pass  # nulls are just ignored.
        else:
            self.dispatch("print", char)

    def consume(self, char):
        """Consume a single character and advance the state as necessary."""
        handler = {
            "stream": self._stream,
            "escape": self._escape_sequence,
            "escape-lb": self._escape_parameters,
            "mode": self._mode,
            "charset-g0": self._charset_g0,
            "charset-g1": self._charset_g1
        }.get(self.state)

        handler and handler(char)

    def process(self, chars):
        """Consume a string of chars and advance the state as necessary."""
        map(self.consume, chars)

    def connect(self, event, callback):
        """Add an event listener for a particular event.

        Depending on the event, there may or may not be parameters
        passed to the callback. Most escape streams also allow for
        an empty set of parameters (with a default value). Providing
        these default values and accepting variable arguments is the
        responsibility of the callback.

        :param event: event to listen for.
        :param function: callable to invoke when a given event occurs.
        """
        self.listeners[event].append(callback)

    def dispatch(self, event, *args):
        """Dispatch an event.

        :param event: event to dispatch.
        :param args: a tuple of the arguments to send to any callbacks.

        .. note::

           If any callback throws an exception, the subsequent callbacks
           will be aborted.
        """
        if event not in self.listeners:
            print("oh shoot -- nobody needs me! (%s, %s)" % (event, args))
        elif event != "print":
            print(event, args)

        for callback in self.listeners.get(event, []):
            if args:
                callback(*args)
            else:
                callback()


class screen(object):
    """
    A screen is an in memory buffer of strings that represents the screen
    display of the terminal. It can be instantiated on it's own and given
    explicit commands, or it can be attached to a stream and will respond
    to events.

    The screen buffer can be accessed through the screen's `display` property.
    """

    #: Default colors and styling. The value of this attribute should
    #: always be immutable, since shallow copies are made when resizing /
    #: applying / deleting / printing.
    #:
    #: Attributes are represented by a three-tuple that consists of the
    #: following:
    #:
    #:     1. A tuple of all the text attributes: `bold`, `underline`, etc
    #:     2. The foreground color as a string, see
    #:        :attr:`vt102.graphics.colors`
    #:     3. The background color as a string, see
    #:        :attr:`vt102.graphics.colors`
    default_attributes = (), "default", "default"

    #: Terminal dimensions and coordinates (we can declare them on the
    #: class level since int-attributes are immutable anyway).
    lines, columns, x, y = (0, ) * 4

    #: Top and bottom margins, defining the scrolling region; the actual
    #: values are top and bottom line.
    margins = namedtuple("margins", "x y")(0, 0)

    def __init__(self, *size):
        self.display = []
        self.attributes = []
        self.tabstops = []

        self.g0 = None
        self.g1 = None
        self.current_charset = "g0"

        self.cursor_save_stack = []
        self.cursor_attributes = self.default_attributes

        if all(size):
            self.resize(*size)
        else:
            raise ValueError("Invalid screen dimensions: %rx%r" % size)

    def __repr__(self):
        return repr([l.tounicode() for l in self.display])

    def attach(self, events):
        """Attach this screen to a events that processes commands and
        dispatches events. Sets up the appropriate event handlers so
        that the screen will update itself automatically as the events
        processes data.
        """
        handlers = [
            ("reset", self._reset),
            ("print", self._print),
            ("backspace", self._backspace),
            ("tab", self._tab),
            ("linefeed", self._linefeed),
            ("reverse-linefeed", self._reverse_linefeed),
            ("carriage-return", self._carriage_return),
            ("save-cursor", self._save_cursor),
            ("restore-cursor", self._restore_cursor),
            ("cursor-up", self._cursor_up),
            ("cursor-down", self._cursor_down),
            ("cursor-forward", self._cursor_forward),
            ("cursor-back", self._cursor_back),
            ("cursor-down1", self._cursor_down1),
            ("cursor-up1", self._cursor_up1),
            ("cursor-position", self._cursor_position),
            ("cursor-to-column", self._cursor_to_column),
            ("cursor-to-line", self._cursor_to_line),
            ("erase-in-line", self._erase_in_line),
            ("erase-in-display", self._erase_in_display),
            ("insert-lines", self._insert_line),
            ("delete-lines", self._delete_line),
            ("delete-characters", self._delete_character),
            ("erase-characters", self._erase_character),
            ("shift-in", self._shift_in),
            ("shift-out", self._shift_out),
            ("select-graphic-rendition", self._select_graphic_rendition),
            ("bell", self._bell),
            ("set-tab-stop", self._set_tab_stop),
            ("clear-tab-stop", self._clear_tab_stop),
            ("set-margins", self._set_margins),
            ("answer", self._answer),

            # Not implemented
            # ...............
            # ("insert-characters", self._insert_characters)
            # ("set-mode", ...)
            # ("reset-mode", ...)
            # ("status-report", ...)
        ]

        for event, handler in handlers:
            events.connect(event, handler)

    def cursor(self):
        """The current location of the cursor."""
        return self.x, self.y

    def resize(self, lines, columns):
        """Resize the screen.

        If the requested screen size has more lines than the existing
        screen, lines will be added at the bottom. If the requested
        size has less lines than the existing screen lines will be
        clipped at the top of the screen.

        Similarly if the existing screen has less columns than the
        requested size, columns will be added at the right, and it it
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

    def _set_margins(self, top=0, bottom=0):
        self.margins.top, self.margins.bottom = 0, 0

    def _answer(self):
        map(self._print, u"%s6c" % ctrl.CSI)

    def _reset(self):
        size = self.lines, self.columns
        self.lines, self.columns = 0, 0
        self.display = []
        self.resize(*size)

        self._home()
        self._set_margins()

    def _shift_in(self):
        self.current_charset = "g0"

    def _shift_out(self):
        self.current_charset = "g1"

    def _charset_g0(self, cs):
        if cs == '0':
            self.g0 = dsg
        else:
            # TODO: Officially support UK/US/intl8 charsets
            self.g0 = None

    def _charset_g1(self, cs):
        if cs == '0':
            self.g1 = dsg
        else:
            # TODO: Officially support UK/US/intl8 charsets
            self.g1 = None


    def _print(self, char):
        """Print a character at the current cursor position and advance
        the cursor.
        """
        if self.current_charset == "g0" and self.g0 is not None:
            char = char.translate(self.g0)
        elif self.current_charset == "g1" and self.g1 is not None:
            char = char.translate(self.g1)

        self.display[self.y][self.x] = char
        self.attributes[self.y][self.x] = self.cursor_attributes

        # .. note:: We can't use :meth:`_cursor_forward()`, because that
        #           way, we'll never know when to linefeed.
        self.x += 1

        # If this was the last column in a line, move the cursor to
        # the next line.
        if self.x == self.columns:
            self._linefeed()

    def _carriage_return(self):
        """Move the cursor to the beginning of the current line."""
        self._cursor_to_column(0)

    def _index(self):
        """Move the cursor down one line in the same column. If the
        cursor is at the last line, create a new line at the bottom.
        """
        if self.y == self.lines - 1:
            top, bottom = self.margins
            self.display.pop(top + 1)
            self.display.insert(bottom - 1,
                                array("u", u" " * self.columns))
        else:
            self._cursor_down()

    def _reverse_index(self):
        """Move the cursor up one line in the same column. If the cursor
        is at the first line, create a new line at the top.
        """
        if not self.y:
            top, bottom = self.margins
            self.display.insert(top + 1, array("u", u" " * self.columns))
            self.display.pop(bottom - 1)
        else:
            self._cursor_up()

    def _linefeed(self):
        """Performs an index and then a carriage return."""
        self._index()
        self._carriage_return()

    def _reverse_linefeed(self):
        """Performs a reverse index and then a carriage return."""
        self._reverse_index()
        self._carriage_return()

    def _next_tab_stop(self):
        """Return the x value of the next available tabstop or the x
        value of the margin if there are no more tabstops.
        """
        for stop in sorted(self.tabstops):
            if self.x < stop:
                return stop
        return self.columns - 1

    def _tab(self):
        """Move to the next tab space, or the end of the screen if there
        aren't anymore left.
        """
        self.x = self._next_tab_stop()

    def _backspace(self):
        """Move cursor to the left one or keep it in it's position if
        it's at the beginning of the line already.
        """
        self._cursor_back()

    def _save_cursor(self):
        """Push the current cursor position onto the stack.

        .. todo:: Save whole screen, not just cursor positions.
        """
        self.cursor_save_stack.append((self.x, self.y))

    def _restore_cursor(self):
        """Set the current cursor position to whatever cursor is on top
        of the stack.
        """
        if self.cursor_save_stack:
            # .. todo:: use _cursor_position()
            self.x, self.y = self.cursor_save_stack.pop()

    def _insert_line(self, count=1):
        """Inserts `count` lines at line with cursor. Lines displayed
        below cursor move down. Lines moved past the bottom margin are
        lost.

        .. todo:: reset attributes at ``self.y`` as well?
        """
        initial = u" " * self.columns

        for line in xrange(self.y, self.y + count):
            self.display.insert(line, array("u", initial))

        while len(self.display) > self.lines:
            self.display.pop(-1)

    def _delete_line(self, count=1):
        """Deletes `count` lines, starting at line with cursor. As lines
        are deleted, lines displayed below cursor move up. Lines added
        to bottom of screen have spaces with same character attributes
        as last line moved up.
        """
        initial = u" " * self.columns

        for line in xrange(self.y, self.y + count):
            self.display.pop(line)
            self.attributes.pop(line)

        while len(self.display) < self.lines:
            self.display.append(array("u", initial))
            self.attributes.append(copy(self.attributes[-1]))

    def _delete_character(self, count=1):
        """Deletes `count` characters, starting with the character at
        cursor position. When a character is deleted, all characters to
        the right of cursor move left.
        """
        count = min(count, self.columns - self.x)

        # First resize the text display ...
        line = self.display[self.y]
        self.display[self.y] = (line[:self.x] +
                                line[self.x + count:] +
                                array("u", u" " * count))

        # .. then resize the attribute array too.
        attrs = self.attributes[self.y]
        self.attributes[self.y] = (attrs[:self.x] +
                                   attrs[self.x + count:] +
                                   [self.default_attributes] * count)

    def _erase_character(self, count=1):
        """Erases `count` characters, starting with the character at
        cursor position.
        """
        for column in xrange(self.x, min(self.x + count,
                                         self.columns)):
            self.display[self.y][column] = u" "
            self.attributes[self.y][column] = self.default_attributes

    def _erase_in_line(self, type_of=0):
        """Erases a line in a specific way, depending on the `type_of`.

        .. todo:: this is still a mess -- somebody, rewrite me!
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

    def _erase_in_display(self, type_of=0):
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

    def _set_tab_stop(self):
        """Sest a horizontal tab stop at cursor position."""
        self.tabstops.append(self.x)

    def _clear_tab_stop(self, type_of=0x33):
        if type_of == 0x30:
            # Clears a horizontal tab stop at cursor position.
            try:
                self.tabstops.remove(self.x)
            except ValueError:
                # If there is no tabstop at the current position, then just do
                # nothing.
                pass
        elif type_of == 0x33:
            # Clears all horizontal tab stops
            self.tabstops = []

    def _cursor_up(self, count=1):
        """Moves cursor up count lines in same column. Cursor stops
        at top margin.
        """
        self._cursor_to_line(self.y - count)

    def _cursor_up1(self, count=1):
        """Moves cursor up count lines to column 1. Cursor stops at
        bottom margin.
        """
        self._cursor_up(count)
        self._carriage_return()

    def _cursor_down(self, count=1):
        """Moves cursor down count lines in same column. Cursor stops
        at bottom margin.
        """
        self._cursor_to_line(self.y + count)

    def _cursor_down1(self, count=1):
        """Moves cursor down count lines to column 1. Cursor stops at
        bottom margin.
        """
        self._cursor_down(count)
        self._carriage_return()

    def _cursor_back(self, count=1):
        """Moves cursor left count columns. Cursor stops at left
        margin.
        """
        self._cursor_to_column(self.x - count)

    def _cursor_forward(self, count=1):
        """Moves cursor right count columns. Cursor stops at right
        margin.
        """
        self._cursor_to_column(self.x + count)

    def _cursor_position(self, line=0, column=0):
        """Set the cursor to a specific line and column.

        .. note::

           Obnoxiously, line and column are 1-based, instead of zero
           based, so we need to compensate. Confoundingly, inputs of 0
           are still acceptable, and should move to the beginning of
           the line or column as if they were 1 -- *sigh*.
        """
        self._cursor_to_line((line or 1) - 1)
        self._cursor_to_column((column or 1) - 1)

    def _cursor_to_column(self, column=0):
        """Set the cursor to a specific column in the current line."""
        self.x = min(max(0, column), self.columns - 1)

    def _cursor_to_line(self, line=0):
        """Set the cursor to a specific line in the current column."""
        self.y = min(max(0, line), self.lines - 1)

    def _home(self):
        """Set the cursor to the left upper corner ``(0, 0)``."""
        self._cursor_position(0, 0)

    def _bell(self, *attrs):
        """Bell stub -- the actual implementation should probably be
        provided by the end-user.
        """
    def _remove_text_attr(self, attr):
        current = set(self.cursor_attributes[0])
        if attr in current:
            current.remove(attr)
        return tuple(current) + self.cursor_attributes[1:]

    def _add_text_attr(self, attr):
        current = set(self.cursor_attributes[0])
        current.add(attr)
        attrs = self.cursor_attributes[1:]
        return (tuple(current), attrs[0], attrs[1])

    def _text_attr(self, attr):
        """
        Given a text attribute, set the current cursor appropriately.
        """
        attr = text[attr]
        if attr == "reset":
            self.cursor_attributes = self.default_attributes
        elif attr == "underline-off":
            self.cursor_attributes = self._remove_text_attr("underline")
        elif attr == "blink-off":
            self.cursor_attributes = self._remove_text_attr("blink")
        elif attr == "reverse-off":
            self.cursor_attributes = self._remove_text_attr("reverse")
        else:
            self.cursor_attributes = self._add_text_attr(attr)

    def _color_attr(self, ground, attr):
        """
        Given a color attribute, set the current cursor appropriately.
        """
        attr = colors[ground][attr]
        attrs = self.cursor_attributes
        if ground == "foreground":
            self.cursor_attributes = (attrs[0], attr, attrs[2])
        elif ground == "background":
            self.cursor_attributes = (attrs[0], attrs[1], attr)

    def _set_attr(self, attr):
        """
        Given some text attribute, set the current cursor attributes
        appropriately.
        """
        if attr in text:
            self._text_attr(attr)
        elif attr in colors["foreground"]:
            self._color_attr("foreground", attr)
        elif attr in colors["background"]:
            self._color_attr("background", attr)

    def _select_graphic_rendition(self, *attrs):
        """
        Set the current text attribute.
        """

        if not attrs:
            # No arguments means that we're really trying to do a reset.
            attrs = [0]

        for attr in attrs:
            self._set_attr(attr)
