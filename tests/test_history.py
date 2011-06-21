# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import operator

from vt102 import HistoryScreen


def chars(lines):
    return ["".join(map(operator.attrgetter("data"), line))
            for line in lines]


def test_index():
    screen = HistoryScreen(5, 5, pages=10)

    # Filling the screen with line numbers, so it's easier to
    # track history contents.
    for idx in xrange(len(screen)):
        screen.draw(unicode(idx))
        if idx is not len(screen) - 1:
            screen.linefeed()

    assert not screen.history.top
    assert not screen.history.bottom

    # a) first index, expecting top history to be updated.
    line = screen[0]
    screen.index()
    assert screen.history.top
    assert screen.history.top[-1] == line

    # b) second index.
    line = screen[0]
    screen.index()
    assert len(screen.history.top) == 2
    assert screen.history.top[-1] == line

    # c) rotation.
    for _ in xrange(len(screen) * screen.lines):
        screen.index()

    assert len(screen.history.top) == 25  # pages // 2 * lines


def test_page_up():
    screen = HistoryScreen(4, 4, pages=10)

    # Once again filling the screen with line numbers, but this time,
    # we need them to span on multiple lines.
    for idx in xrange(len(screen) * 10):
        map(screen.draw, unicode(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.page == 5
    assert screen.display == [
        "37  ",
        "38  ",
        "39  ",
        "    "
    ]

    assert chars(screen.history.top)[-4:] == [
        "33  ",
        "34  ",
        "35  ",
        "36  "
    ]

    # a) first page up.
    screen.page_up()
    assert screen.page == 4
    assert screen.display == [
        "35  ",
        "36  ",
        "37  ",
        "38  "
    ]

    assert chars(screen.history.top)[-4:] == [
        "31  ",
        "32  ",
        "33  ",
        "34  "
    ]

    assert len(screen.history.bottom) == 2
    assert chars(screen.history.bottom) == [
        "39  ",
        "    ",
    ]

    # b) second page up.
    screen.page_up()
    assert screen.page == 3
    assert screen.display == [
        "33  ",
        "34  ",
        "35  ",
        "36  ",
    ]

    assert len(screen.history.bottom) == 4
    assert chars(screen.history.bottom) == [
        "37  ",
        "38  ",
        "39  ",
        "    ",
    ]

    # c) same with odd number of lines.
    screen = HistoryScreen(5, 5, pages=10)

    # Once again filling the screen with line numbers, but this time,
    # we need them to span on multiple lines.
    for idx in xrange(len(screen) * 10):
        map(screen.draw, unicode(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.page == 5
    assert screen.display == [
        "46   ",
        "47   ",
        "48   ",
        "49   ",
        "     "
    ]

    screen.page_up()
    assert screen.page == 4
    assert screen.display == [
        "43   ",
        "44   ",
        "45   ",
        "46   ",
        "47   "
    ]

    assert len(screen.history.bottom) == 3
    assert chars(screen.history.bottom) == [
        "48   ",
        "49   ",
        "     ",
    ]



def test_page_down():
    screen = HistoryScreen(5, 5, pages=10)

    # Once again filling the screen with line numbers, but this time,
    # we need them to span on multiple lines.
    for idx in xrange(len(screen) * 5):
        map(screen.draw, unicode(idx))
        screen.linefeed()

    assert screen.history.top
    assert not screen.history.bottom
    assert screen.page == 5
    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "     "
    ]

    # a) page up -- page down.
    screen.page_up()
    screen.page_down()
    assert screen.history.top
    assert not screen.history.bottom
    assert screen.page == 5
    assert screen.display == [
        "21   ",
        "22   ",
        "23   ",
        "24   ",
        "     "
    ]

    # b) double page up -- page down.
    screen.page_up()
    screen.page_up()
    screen.page_down()
    assert screen.page == 4
    assert screen.history.top
    assert chars(screen.history.bottom) == [
        "23   ",
        "24   ",
        "     "
    ]

    assert screen.display == [
        "18   ",
        "19   ",
        "20   ",
        "21   ",
        "22   "
    ]


    # c) double page up -- double page down
    screen.page_up()
    screen.page_up()
    screen.page_down()
    screen.page_down()
    assert screen.page == 4
    assert screen.display == [
        "18   ",
        "19   ",
        "20   ",
        "21   ",
        "22   "
    ]
