vt102
=====

:Info: Scrap'in on my scrapper screen.
:Author: Sam Gibson <sam@ifdown.net>


About
-----

``vt102`` is an in memory vt102 terminal emulator. It supports all the
most common terminal escape sequences, including text attributes and
color.

Why would you want to use a terminal emulator?

* Screen scraping some terminal or curses app.
* Chicks dig dudes with terminals.
* ... seriously, that's about it.


Installation
------------

If you have `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
you can use ``easy_install -U vt102``. Otherwise, you can download the source
from `GitHub <http://github.com/samfoo/vt102>`_ and run ``python setup.py install``.


Example
-------

    >>> import vt102
    >>> stream = vt102.stream()
    >>> screen = vt102.screen(24, 80)
    >>> screen.attach(stream)
    >>> stream.process(u"\u001b7\u001b[?47h\u001b)0\u001b[H\u001b[2J\u001b[H"
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
