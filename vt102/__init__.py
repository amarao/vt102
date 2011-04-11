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

__all__ = ("screen", "stream", "ctrl", "esc")

from . import control as ctrl, escape as esc
from .screen import screen
from .stream import stream



