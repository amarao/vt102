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
    ...
    ...     def up(self, bar):
    ...         self.foo += bar
    ...
    >>> dummy = Dummy()
    >>> stream = vt102.Stream()
    >>> stream.connect("cursor-up", dummy.up)
    >>> stream.feed(u"\u001B[5A") # Move the cursor up 5 rows.
    >>> dummy.foo
    5

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

from __future__ import absolute_import

import codecs
import sys
from collections import defaultdict

from . import control as ctrl, escape as esc


class Stream(object):
    """A stream is a state machine that parses a stream of characters
    and dispatches events based on what it sees.

    .. note::

       Stream only accepts unicode strings as input, but if, for some
       reason, you need to feed it with byte strings, consider using
       :class:`vt102.streams.ByteStream` instead.

    .. seealso::

        `man console_codes <http://linux.die.net/man/4/console_codes>`_
            For details on console codes listed bellow in :attr:`basic`,
            :attr:`escape`, :attr:`csi` and :attr:`sharp`.
    """

    #: Control sequences, which don't require any arguments.
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
    }

    #: "sharp" escape sequences -- ``ESC # <N>``.
    sharp = {
        esc.DECALN: "alignment-display",
    }

    #: CSI escape sequences -- ``CSI P1;P2;...;Pn <fn>``.
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
        esc.HPR: "cursor-forward",
        esc.VPA: "cursor-to-line",
        esc.VPR: "cursor-down",
        esc.HVP: "cursor-position",
        esc.TBC: "clear-tab-stop",
        esc.SM: "set-mode",
        esc.RM: "reset-mode",
        esc.SGR: "select-graphic-rendition",
        esc.DECSTBM: "set-margins",
        esc.HPA: "cursor-to-column",
    }

    def __init__(self):
        self.handlers = {
            "stream": self._stream,
            "escape": self._escape,
            "arguments": self._arguments,
            "sharp": self._sharp
        }

        self.listeners = defaultdict(lambda: [])
        self.reset()

    def reset(self):
        """Reset state to ``"stream"`` and empty parameter attributes."""
        self.state = "stream"
        self.flags = {}
        self.params = []
        self.current = u""

    def consume(self, char):
        """Consume a single unicode character and advance the state as
        necessary.

        :param unicode char: a unicode character to consume.
        """
        if not isinstance(char, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        try:
            self.handlers.get(self.state)(char)
        except TypeError:
            pass

    def feed(self, chars):
        """Consume a unicode string and advance the state as necessary.

        :param unicode chars: a unicode string to feed from.
        """
        if not isinstance(chars, unicode):
            raise TypeError(
                "%s requires unicode input" % self.__class__.__name__)

        for char in chars: self.consume(char)

    def connect(self, event, callback):
        """Add an event listener for a particular event.

        Depending on the event, there may or may not be parameters
        passed to the callback. Some escape sequences might also have
        default values, but providing these defaults is responsibility
        of the callback.

        :param unicode event: event to listen for.
        :param callable callback: callable to invoke when a given event
                                  occurs.
        """
        self.listeners[event].append(callback)

    def dispatch(self, event, *args, **flags):
        """Dispatch an event.

        .. note::

           If any callback throws an exception, the subsequent callbacks
           are be aborted.

        :param unicode event: event to dispatch.
        :param list args: arguments to pass to event handlers.
        :param dict flags: keyword flags to pass to event handlers.
        """
        for callback in self.listeners.get(event, []):
            callback(*args, **flags)

    # State transformers.
    # ...................

    def _stream(self, char):
        """Process a character when in the default ``"stream"`` state."""
        if char in self.basic:
            self.dispatch(self.basic[char])
        elif char == ctrl.ESC:
            self.state = "escape"
        elif char == ctrl.CSI:
            self.state = "arguments"
        elif char not in (ctrl.NUL, ctrl.DEL):
            self.dispatch("draw", char)

    def _escape(self, char):
        """Handle characters seen when in an escape sequence.

        Most non-VT52 commands start with a left-bracket after the
        escape and then a stream of parameters and a command; with
        a single notable exception -- :data:`escape.DECOM` sequence,
        which starts with a sharp.
        """
        if char == u"#":
            self.state = "sharp"
        elif char == u"[":
            self.state = "arguments"
        elif char in self.escape:
            self.state = "stream"
            self.dispatch(self.escape[char])
        else:
            self.state = "stream"

    def _sharp(self, char):
        """Parse arguments of a `"#"` seqence."""
        if char in self.sharp:
            self.dispatch(self.sharp[char])

        self.state = "stream"

    def _arguments(self, char):
        """Parse arguments of an escape sequence.

        All parameters are unsigned, positive decimal integers, with
        the most significant digit sent first. Any parameter greater
        than 9999 is set to 9999. If you do not specify a value, a 0
        value is assumed.

        .. seealso::

           `VT102 User Guide <http://vt100.net/docs/vt102-ug/>`_
               For details on the formatting of escape arguments.

           `VT220 Programmer Reference <http://http://vt100.net/docs/vt220-rm/>`_
               For details on the characters valid for use as arguments.
        """
        if char == u"?":
            self.flags["private"] = True
        elif char in [ctrl.BEL, ctrl.BS, ctrl.HT, ctrl.LF, ctrl.CR]:
            # Not sure why, but those seem to be allowed between CSI
            # sequence arguments.
            pass
        elif char in [ctrl.CAN, ctrl.SUB]:
            # If CAN or SUB is received during a sequence, the current
            # sequence is aborted; terminal displays the substitute
            # character, followed by characters in the sequence received
            # after CAN or SUB.
            self.dispatch("draw", char)
            self.state = "stream"
        elif char.isdigit():
            self.current += char
        else:
            self.params.append(min(int(self.current or 0), 9999))

            if char == u";":
                self.current = u""
            else:
                event = self.csi.get(char)
                if event:
                    self.dispatch(event, *self.params, **self.flags)
                elif __debug__:
                    self.dispatch("debug",
                        ctrl.CSI + u";".join(map(unicode, self.params)) + char)

                self.reset()


class ByteStream(Stream):
    """Stream, which takes byte strings (instead of unicode) as input.
    It uses :class:`codecs.IncrementalDecoder` to decode bytes fed into
    a predefined encoding, so broken bytes is not an issue.

    >>> stream = ByteStream()
    >>> stream.feed(b"foo".decode("utf-8"))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "vt102/streams.py", line 288, in feed
        "%s requires input in bytes" % self.__class__.__name__)
    TypeError: ByteStream requires input in bytes
    >>> stream.feed(b"foo")

    :param unicode encoding: input encoding.
    :param unicode errors: how to handle decoding errors, see
                           :meth:`str.decode` for possible values.
    """

    def __init__(self, encoding="utf-8", errors="replace"):
        self.decoder = codecs.getincrementaldecoder(encoding)(errors)
        super(ByteStream, self).__init__()

    def feed(self, chars):
        if not isinstance(chars, bytes):
            raise TypeError(
                "%s requires input in bytes" % self.__class__.__name__)

        super(ByteStream, self).feed(self.decoder.decode(chars))


class DebugStream(ByteStream):
    """Stream, which dumps a subset of the dispatched events to a given
    file-like object (:data:`sys.stdout` by default).

    >>> stream = DebugStream()
    >>> stream.feed("\x1b[1;24r\x1b[4l\x1b[24;1H\x1b[0;10m")
    SET-MARGINS 1, 24
    RESET-MODE 4
    CURSOR-POSITION 24, 1
    SELECT-GRAPHIC-RENDITION 0, 10

    :param file to: a file-like object to write debug information to.
    :param list only: a list of events you want to debug (empty by
                      default, which means -- debug all events).
    """

    def __init__(self, to=sys.stdout, only=(), *args, **kwargs):
        self.to = to
        self.only = set(only)
        super(DebugStream, self).__init__(*args, **kwargs)

    def dispatch(self, event, *args, **kwargs):
        if not self.only or event in self.only:
            self.to.write("%s " % event.upper())

            for arg in args:
                if isinstance(arg, unicode):
                    arg = arg.encode("utf-8")
                elif not isinstance(arg, bytes):
                    arg = bytes(arg)

                self.to.write("%s " % arg)
            else:
                self.to.write("\n")

        super(DebugStream, self).dispatch(event, *args, **kwargs)
