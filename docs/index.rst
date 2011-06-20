.. vt102 documentation master file, created by
   sphinx-quickstart on Fri Apr  8 12:49:51 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to vt102's documentation!
=================================

What is ``vt102``? It's an in memory VTXXX-compatible terminal emulator.
*XXX* stands for a series video terminals, developed by
`DEC <http://en.wikipedia.org/wiki/Digital_Equipment_Corporation>`_ between
1970 and 1995. The first, and probably the most famous one, was VT100
terminal, which is now a de-facto standard for all virtual terminal
emulators. ``vt102`` follows the suit.

So, why would one need a terminal emulator library?

* To screen scrape terminal apps, for example ``htop`` or ``aptitude``.
* To write cross platform terminal emulators; either with a graphical
  (`xterm <http://invisible-island.net/xterm/>`_,
  `rxvt <http://www.rxvt.org/>`_) or a web interface, like
  `AjaxTerm <http://antony.lesuisse.org/software/ajaxterm/>`_.
* To have fun, hacking on the ancient, poorly documented technologies.


.. todolist::


Usage
=====

There are two important classes in ``vt102``:
:class:`~vt102.screens.Screen` and :class:`~vt102.streams.Stream`. The
``Screen`` is the terminal screen emulator. It maintains an in-memory
buffer of text and text-attributes to display on screen. The ``Stream``
is the stream processor. It manages the state of the input and dispatches
events to anything that's listening about things that are going on.
Events are things like ``LINEFEED``, ``DRAW "a"``, or ``CURSOR_POSITION 10 10``.
See the :ref:`API <api>` for more details.

In general, if you just want to know what's being displayed on screen you
can do something like the following:

    >>> import vt102
    >>> screen = vt102.Screen(80, 24)
    >>> stream = vt102.Stream()
    >>> stream.attach(screen)
    >>> stream.feed(u"\u001b7\u001b[?47h\u001b)0\u001b[H\u001b[2J\u001b[H"
                    u"\u001b[2;1HNetHack, Copyright 1985-2003\r\u001b[3;1"
                    u"H         By Stichting Mathematisch Centrum and M. "
                    u"Stephenson.\r\u001b[4;1H         See license for de"
                    u"tails.\r\u001b[5;1H\u001b[6;1H\u001b[7;1HShall I pi"
                    u"ck a character's race, role, gender and alignment f"
                    u"or you? [ynq] ")
    >>> screen.display
        ['                                                                                ',
         'NetHack, Copyright 1985-2003                                                    ',
         '         By Stichting Mathematisch Centrum and M. Stephenson.                   ',
         '         See license for details.                                               ',
         '                                                                                ',
         '                                                                                ',
         "Shall I pick a character's race, role, gender and alignment for you? [ynq]      ",
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ',
         '                                                                                ']
    >>>

.. _api:

API
===

.. automodule:: vt102.streams
    :members:

.. automodule:: vt102.screens
    :members:

.. automodule:: vt102.modes
    :members:

.. automodule:: vt102.control
    :members:

.. automodule:: vt102.escape
    :members:

.. automodule:: vt102.graphics
    :members:

.. automodule:: vt102.charsets
    :members:
