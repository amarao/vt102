# -*- coding: utf-8 -*-
"""
    vt102
    ~~~~~

    `vt102` implements a mix of VT102, VT220 and VT520 specification,
    an aims to support most of the `TERM=linux` functionality.

    Two classes: :class:`vt102.Stream`, which parses the command stream
    and dispatches events for commands, and :class:`vt102.Screen` which,
    when used with a `Stream` maintains a buffer of strings representing
    the screen of a terminal.

    :copyright: (c) 2011 by Selectel, see AUTHORS for more details.
    :license: LGPL, see LICENSE for more details.
"""

__all__ = ("Screen", "Stream", "ByteStream", "DebugStream",
           "ctrl", "esc", "mo", "g")

from . import control as ctrl, escape as esc, modes as mo, graphics as g
from .screens import Screen
from .streams import Stream, ByteStream, DebugStream


if __debug__:
    def dis(chars):
        """A :func:`dis.dis` for terminals.

        >>> dis(u"\u0007")
        BELL
        >>> dis(u"\x9b20m")
        SELECT-GRAPHIC-RENDITION 20
        """
        if isinstance(chars, unicode):
            chars = chars.encode("utf-8")

        return DebugStream().feed(chars)
