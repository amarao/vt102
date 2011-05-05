# -*- coding: utf-8 -*-
"""
    vt102.streams
    ~~~~~~~~~~~~~

    Quick example:

    >>> import vt102
    >>>
    >>> class Dummy(object):
    ...     def __init__(self):
    ...         self.foo = 0
    ...     def up(self, bar):
    ...         self.foo += bar
    ...
    >>> dummy = Dummy()
    >>> stream = vt102.Stream()
    >>> stream.connect("cursor-up", dummy.up)
    >>>
    >>> stream.feed(u"\u001B[5A") # Move the cursor up 5 rows.
    >>> dummy.foo
    5

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import absolute_import

import codecs
from warnings import warn
from collections import defaultdict

from . import control as ctrl, escape as esc


class Stream(object):
    """A stream is a state machine that parses a stream of terminal
    characters and dispatches events based on what it sees.

    .. note::

       Stream only accepts unicode strings as input, but if for some
       reason you need to feed it with byte strings, use
       :class:`vt102.streams.ByteStream`.

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow in :attr:`basic`,
            :attr:`escape`, :attr:`csi`
    """

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

    #: non-CSI escape sequences.
    escape = {
        esc.RIS: "reset",
        esc.IND: "index",
        esc.NEL: "linefeed",
        esc.RI: "reverse-index",
        esc.HTS: "set-tab-stop",
        esc.DECSC: "save-cursor",
        esc.DECRC: "restore-cursor",
        esc.DECALN: "alignment-display",
    }

    #: CSI escape sequences.
    csi = {
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
        """Reset state to ``"stream"`` and empty parameter attributes."""
        self.state = "stream"
        self.params = []
        self.current = ""

    def consume(self, char):
        """Consume a single unicode character and advance the state as
        necessary.

        :param char: a unicode character to consume.
        """
        if not isinstance(char, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        handler = {
            "stream": self._stream,
            "escape": self._escape,
            "arguments": self._arguments,
        }.get(self.state)

        handler and handler(char)

    def feed(self, chars):
        """Consume a unicode string and advance the state as necessary.

        :param chars: a unicode string to feed from.
        """
        if not isinstance(chars, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        map(self.consume, chars)

    def connect(self, event, callback):
        """Add an event listener for a particular event.

        Depending on the event, there may or may not be parameters
        passed to the callback. Some escape sequences might also have
        default values, but providing these defaults is responsibility
        of the callback.

        :param event: event to listen for.
        :param function: callable to invoke when a given event occurs.
        """
        self.listeners[event].append(callback)

    def dispatch(self, event, *args):
        """Dispatch an event.

        :param event: event to dispatch.
        :param args: a tuple of arguments to send to each callback.

        .. note::

           If any callback throws an exception, the subsequent callbacks
           are be aborted.
        """
        if event not in self.listeners:
            warn("no listner found for %s(%s)" % (event, args))

        for callback in self.listeners.get(event, []):
            if args:
                callback(*args)
            else:
                callback()

    # State transformers.
    # ...................

    def _stream(self, char):
        """Process a character when in the default ``"stream"`` state."""
        num = ord(char)
        if num in self.basic:
            self.dispatch(self.basic[num])
        elif num == ctrl.ESC:
            self.state = "escape"
        elif num == ctrl.CSI:
            self.state = "arguments"
        elif not num:
            pass  # nulls are just ignored.
        else:
            self.dispatch("draw", char)

    def _escape(self, char):
        """Handle characters seen when in an escape sequence.

        Most non-VT52 commands start with a left-bracket after the
        escape and then a stream of parameters and a command; with
        a single notable exception -- :data:`escape.DECOM` sequence,
        which starts with a sharp.
        """
        if char == "#":
            pass
        elif char == "[":
            self.state = "arguments"
        elif ord(char) in self.escape:
            self.state = "stream"
            self.dispatch(self.escape[ord(char)])
        else:
            self.state = "stream"

    def _arguments(self, char):
        """Parse arguments of an escape sequence.

        Parameters are a list of numbers in ASCII (e.g. ``12``, ``4``,
        ``42``, etc) separated by a semicolon (e.g. ``12;4;42``). If
        any of the given param is not a number it's skipped silently.

        .. seealso::

           `VT102 User Guide <http://vt100.net/docs/vt102-ug/>`_
               For details on the formatting of escape arguments.

           `VT220 Programmer Reference <http://http://vt100.net/docs/vt220-rm/>`_
               For details on the characters valid for use as arguments.
        """
        if char == "?":
            # At this point we don't distinguish DEC private modes from
            # ANSI modes, since the latter are pretty much useless for
            # a library to handle.
            pass
        elif char.isdigit():
            # .. todo: joining strings with `+` is way too slow!
            self.current += char
        else:
            self.current and self.params.append(int(self.current))

            if char == ";":
                self.current = ""
            else:
                event = self.csi.get(ord(char))
                if event:
                    self.dispatch(event, *self.params)
                else:
                    self.dispatch("debug",
                                  unichr(ctrl.CSI) +
                                  u";".join(map(unicode, self.params)) + char)

                self.reset()


class ByteStream(Stream):
    """Stream, which takes byte strings (instead of unicode) as input.
    It uses :class:`codecs.IncrementalDecoder` to decode bytes fed into
    a predefined encoding, so broken bytes is not an issue.

    :param encoding: input encoding.
    """

    def __init__(self, encoding="utf-8"):
        self.decoder = codecs.getincrementaldecoder(encoding)()
        super(ByteStream, self).__init__()

    def feed(self, chars):
        if not isinstance(chars, bytes):
            raise TypeError(
                "%s requires input in bytes" % self.__class__.__name__)

        super(ByteStream, self).feed(self.decoder.decode(chars))
