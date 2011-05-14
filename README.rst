vt102
=====

«Chicks dig dudes with terminals» © `@samfoo <http://github.com/samfoo>`_


About
-----

``vt102`` is an in-memory VTXXX-compatible terminal emulator. Like almost
`all <http://sourceforge.net/projects/termemulator>`_
`of <http://hg.logilab.org/pyqonsole/file/bf7fb8ce56a1/pyqonsole/emuVt102.py>`_
`the <http://code.google.com/p/webtty/source/browse/trunk/lib/app_comet.py>`_
pure-Python VT100 emulation labraries, it claims to «support all the most
common terminal escape sequences, including text attributes, color and more!».


Installation
------------

If you have `setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
you can use ``easy_install -U vt102``. Otherwise, you can download the source
from `GitHub <http://github.com/samfoo/vt102>`_ and run ``python setup.py install``.


Example
-------

    >>> import vt102
    >>> stream = vt102.Stream()
    >>> screen = vt102.Screen(80, 24)
    >>> screen.attach(stream)
    >>> stream.feed(u"\u001b7\u001b[?47h\u001b)0\u001b[H\u001b[2J\u001b[H"
                    u"\u001b[2;1HNetHack, Copyright 1985-2003\r\u001b[3;1"
                    u"H         By Stichting Mathematisch Centrum and M. "
                    u"Stephenson.\r\u001b[4;1H         See license for de"
                    u"tails.\r\u001b[5;1H\u001b[6;1H\u001b[7;1HShall I pi"
                    u"ck a character's race, role, gender and alignment f"
                    u"or you? [ynq] ")
    >>> map(lambda l: l.tounicode(), screen.display)
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
