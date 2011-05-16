# -*- coding: utf-8 -*-

from array import array

import pytest

from vt102 import Screen, Stream, mo
from vt102.screens import Attributes

# A shortcut, which converts an iterable yielding byte strings
# to a list of arrays in "utf-8".
_ = lambda lines: [array("u", l.decode("utf-8")) for l in lines]


def test_remove_non_existant_attribute():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.select_graphic_rendition(24)  # underline-off.
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2


def test_attributes():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    screen.select_graphic_rendition(1) # Bold

    # Still default, since we haven't written anything.
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    assert screen.cursor_attributes == ("default", "default", set(["bold"]))

    screen.draw(u"f")
    assert screen.attributes == [
        [("default", "default", set(["bold"])), screen.default_attributes],
        [screen.default_attributes, screen.default_attributes]
    ]


def test_colors():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.select_graphic_rendition(30) # black foreground
    screen.select_graphic_rendition(40) # black background
    assert screen.cursor_attributes == ("black", "black", set())

    screen.select_graphic_rendition(31) # red foreground
    assert screen.cursor_attributes == ("red", "black", set())


def test_reset_resets_colors():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.select_graphic_rendition(30) # black foreground
    screen.select_graphic_rendition(40) # black background
    assert screen.cursor_attributes == ("black", "black", set())

    screen.select_graphic_rendition(0)
    assert screen.cursor_attributes == screen.default_attributes


def test_multi_attribs():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    screen.select_graphic_rendition(1) # Bold
    screen.select_graphic_rendition(3) # Italics

    assert screen.cursor_attributes == \
        ("default", "default", set(["bold", "italics"]))


def test_attributes_reset():
    screen = Screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    screen.select_graphic_rendition(1) # Bold
    screen.draw(u"f")
    screen.draw(u"o")
    screen.draw(u"o")
    assert screen.attributes == [
        [("default", "default", set(["bold"])),
         ("default", "default", set(["bold"]))],
        [("default", "default", set(["bold"])),
         screen.default_attributes],
    ]

    screen.cursor_position()
    screen.select_graphic_rendition(0) # Reset
    screen.draw(u"f")
    assert screen.attributes == [
        [screen.default_attributes, ("default", "default", set(["bold"]))],
        [("default", "default", set(["bold"])), screen.default_attributes],
    ]


def test_resize():
    screen = Screen(2, 2)
    assert repr(screen) == repr([u"  ", u"  "])
    assert screen.attributes == [[screen.default_attributes,
                                  screen.default_attributes]] * 2

    screen.resize(3, 3)
    assert repr(screen) == repr([u"   ", u"   ", u"   "])
    assert screen.attributes == [[screen.default_attributes,
                                  screen.default_attributes,
                                  screen.default_attributes]] * 3

    screen.resize(2, 2)
    assert repr(screen) == repr([u"  ", u"  "])
    assert screen.attributes == [[screen.default_attributes,
                                  screen.default_attributes]] * 2


def test_draw():
    # ``DECAWM`` on (default).
    screen = Screen(3, 3)
    assert mo.DECAWM in screen.mode

    map(screen.draw, u"abc")
    assert repr(screen) == repr([u"abc", u"   ", u"   "])
    assert screen.cursor == (3, 0)

    # ... one` more character -- now we got a linefeed!
    screen.draw(u"a")
    assert screen.cursor == (1, 1)

    # ``DECAWM`` is off.
    screen = Screen(3, 3)
    screen.reset_mode(mo.DECAWM)

    map(screen.draw, u"abc")
    assert repr(screen) == repr([u"abc", u"   ", u"   "])
    assert screen.cursor == (3, 0)

    # No linefeed is issued on the end of the line ...
    screen.draw(u"a")
    assert repr(screen) == repr([u"aba", u"   ", u"   "])
    assert screen.cursor == (3, 0)

    # ``IRM`` mode is on, expecting new characters to move the old ones
    # instead of replacing them.
    screen.set_mode(mo.IRM)
    screen.cursor_position()
    screen.draw(u"x")
    assert repr(screen) == repr([u"xab", u"   ", u"   "])

    screen.cursor_position()
    screen.draw(u"y")
    assert repr(screen) == repr([u"yxa", u"   ", u"   "])


def test_carriage_return():
    screen = Screen(3, 3)
    screen.x = 2
    screen.carriage_return()

    assert screen.x == 0


def test_index():
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    screen.attributes = [[screen.default_attributes] * 2,
                         [Attributes("red", "default", set())] * 2]

    # a) indexing on a row that isn't the last should just move
    # the cursor down.
    screen.index()
    assert screen.cursor == (0, 1)
    assert screen.display == _(["bo", "sh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [Attributes("red", "default", set())] * 2]

    # b) indexing on the last row should push everything up and
    # create a new row at the bottom.
    screen.index()
    assert screen.y == 1
    assert screen.display == _([u"sh", u"  "])
    assert screen.attributes == [[Attributes("red", "default", set())] * 2,
                                 [screen.default_attributes] * 2]

    # c) same with margins
    screen = Screen(2, 5)
    screen.display = _(["bo", "sh", "th", "er", "oh"])
    screen.attributes = [[screen.default_attributes] * 2,
                         [screen.default_attributes] * 2,
                         [Attributes("red", "default", set())] * 2,
                         [Attributes("red", "default", set())] * 2,
                         [screen.default_attributes] * 2]
    screen.set_margins(2, 4)
    screen.y = 3

    # ... go!
    screen.index()
    assert screen.cursor == (0, 3)
    assert screen.display == _([u"bo", u"th", u"er", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [Attributes("red", "default", set())] * 2,
                                 [Attributes("red", "default", set())] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]

    # ... and again ...
    screen.index()
    assert screen.cursor == (0, 3)
    assert screen.display == _([u"bo", u"er", u"  ", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [Attributes("red", "default", set())] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]

    # ... and again ...
    screen.index()
    assert screen.cursor == (0, 3)
    assert screen.display == _([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]

    # look, nothing changes!
    screen.index()
    assert screen.cursor == (0, 3)
    assert screen.display == _([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]


def test_reverse_index():
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    screen.attributes = [[Attributes("red", "default", set())] * 2,
                         [screen.default_attributes] * 2]


    # a) reverse indexing on the first row should push rows down
    # and create a new row at the top.
    screen.reverse_index()
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"  ", u"bo"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [Attributes("red", "default", set())] * 2]

    # b) once again ...
    screen.reverse_index()
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"  ", u"  "])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]

    # c) same with margins
    screen = Screen(2, 5)
    screen.display = _(["bo", "sh", "th", "er", "oh"])
    screen.attributes = [[screen.default_attributes] * 2,
                         [screen.default_attributes] * 2,
                         [Attributes("red", "default", set())] * 2,
                         [Attributes("red", "default", set())] * 2,
                         [screen.default_attributes] * 2]
    screen.set_margins(2, 4)
    screen.y = 1

    # ... go!
    screen.reverse_index()
    assert screen.cursor == (0, 1)
    assert screen.display == _([u"bo", u"  ", u"sh", u"th", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [Attributes("red", "default", set())] * 2,
                                 [screen.default_attributes] * 2]

    # ... and again ...
    screen.reverse_index()
    assert screen.cursor == (0, 1)
    assert screen.display == _([u"bo", u"  ", u"  ", u"sh", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]


    # ... and again ...
    screen.reverse_index()
    assert screen.cursor == (0, 1)
    assert screen.display == _([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]


    # look, nothing changes!
    screen.reverse_index()
    assert screen.cursor == (0, 1)
    assert screen.display == _([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.attributes == [[screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2,
                                 [screen.default_attributes] * 2]



def test_linefeed():
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])

    # a) LNM on by default (that's what `vttest` forces us to do).
    assert mo.LNM in screen.mode
    screen.x, screen.y = 1, 0
    screen.linefeed()
    assert screen.cursor == (0, 1)

    # b) LNM off.
    screen.reset_mode(mo.LNM)
    screen.x, screen.y = 1, 0
    screen.linefeed()
    assert screen.cursor == (1, 1)


def test_tabstops():
    screen = Screen(10, 10)

    # Making sure initial tabstops are in place ...
    assert screen.tabstops == set([7])

    # ... and clearing them.
    screen.clear_tab_stop(3)
    assert not screen.tabstops

    screen.x = 1
    screen.set_tab_stop()
    screen.x = 8
    screen.set_tab_stop()

    screen.x = 0
    screen.tab()
    assert screen.x == 1
    screen.tab()
    assert screen.x == 8
    screen.tab()
    assert screen.x == 9
    screen.tab()
    assert screen.x == 9


def test_clear_tabstops():
    screen = Screen(10, 10)
    screen.clear_tab_stop(3)

    # a) clear a tabstop at current cusor location
    screen.x = 1
    screen.set_tab_stop()
    screen.x = 5
    screen.set_tab_stop()
    screen.clear_tab_stop()

    assert screen.tabstops == set([1])

    screen.set_tab_stop()
    screen.clear_tab_stop(0)

    assert screen.tabstops == set([1])

    # b) all tabstops
    screen.set_tab_stop()
    screen.x = 9
    screen.set_tab_stop()
    screen.clear_tab_stop(3)

    assert not screen.tabstops


def test_resize_shifts_horizontal():
    # If the current display is thinner than the requested size...
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    # New columns should get added to the right.
    screen.resize(2, 3)

    assert repr(screen) == repr([u"bo ", u"sh "])

    # If the current display is wider than the requested size...
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    # Columns should be removed from the right...
    screen.resize(2, 1)

    assert repr(screen) == repr([u"b", u"s"])


def test_backspace():
    screen = Screen(2, 2)
    assert screen.x == 0
    screen.backspace()
    assert screen.x == 0
    screen.x = 1
    screen.backspace()
    assert screen.x == 0


def test_save_cursor():
    # a) cursor position
    screen = Screen(10, 10)
    screen.save_cursor()
    screen.x, screen.y = 3, 5
    screen.save_cursor()
    screen.x, screen.y = 4, 4

    screen.restore_cursor()
    assert screen.x == 3
    assert screen.y == 5

    screen.restore_cursor()
    assert screen.x == 0
    assert screen.y == 0

    # b) modes
    screen = Screen(10, 10)
    screen.set_mode(mo.DECAWM, mo.DECOM)
    screen.save_cursor()

    screen.reset_mode(mo.DECAWM)

    screen.restore_cursor()
    assert mo.DECAWM in screen.mode
    assert mo.DECOM in screen.mode

    # c) attributes
    screen = Screen(10, 10)
    screen.select_graphic_rendition(4)
    screen.save_cursor()
    screen.select_graphic_rendition(24)

    assert screen.cursor_attributes == screen.default_attributes

    screen.restore_cursor()

    assert screen.cursor_attributes != screen.default_attributes
    assert screen.cursor_attributes == ("default", "default", set(["underscore"]))


def test_restore_cursor_with_none_saved():
    screen = Screen(10, 10)
    screen.set_mode(mo.DECOM)
    screen.x, screen.y = 5, 5
    screen.restore_cursor()

    assert screen.cursor == (0, 0)
    assert mo.DECOM not in screen.mode


def test_insert_lines():
    # a) without margins
    screen = Screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.insert_lines()

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"   ", u"sam", u"is "])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3]

    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]
    screen.insert_lines(2)

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"   ", u"   ", u"sam"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3]

    # b) with margins
    screen = Screen(3, 5)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.set_margins(1, 4)
    screen.y = 1
    screen.insert_lines(1)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"   ", u"is ", u"foo", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3]


    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.set_margins(1, 3)
    screen.y = 1
    screen.insert_lines(1)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"   ", u"is ", u"bar",  u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3]


    screen.insert_lines(2)
    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"   ", u"   ", u"bar",  u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3]

    # c) with margins -- trying to insert more than we have available
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.set_margins(2, 4)
    screen.y = 1
    screen.insert_lines(20)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"   ", u"   ", u"   ", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    # d) with margins -- trying to insert outside scroll boundaries;
    #    expecting nothing to change
    screen = Screen(3, 5)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.set_margins(2, 4)
    screen.insert_lines(5)

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"sam", u"is ", u"foo", u"bar", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3]


def test_delete_lines():
    # a) without margins
    screen = Screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.delete_lines()

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"is ", u"foo", u"   "])
    assert screen.attributes == [[Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    screen.delete_lines(0)

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"foo", u"   ", u"   "])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    # b) with margins
    screen = Screen(3, 5)
    screen.set_margins(1, 4)
    screen.y = 1
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.delete_lines(1)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"foo", u"bar", u"   ", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.delete_lines(2)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"bar", u"   ", u"   ", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    # c) with margins -- trying to delete  more than we have available
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.delete_lines(5)

    assert screen.cursor == (0, 1)
    assert screen.display == _([u"sam", u"   ", u"   ", u"   ", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3]

    # d) with margins -- trying to delete outside scroll boundaries;
    #    expecting nothing to change
    screen = Screen(3, 5)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.attributes = [[screen.default_attributes] * 3,
                         [screen.default_attributes] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3]
    screen.set_margins(2, 4)
    screen.delete_lines(5)

    assert screen.cursor == (0, 0)
    assert screen.display == _([u"sam", u"is ", u"foo", u"bar", u"baz"])
    assert screen.attributes == [[screen.default_attributes] * 3,
                                 [screen.default_attributes] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [Attributes("red", "default", set())] * 3,
                                 [screen.default_attributes] * 3]




def test_insert_characters():
    screen = Screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]

    # a) normal case
    cursor = screen.cursor
    screen.insert_characters(2)
    assert screen.cursor == cursor
    assert screen.display == _([u"  s", u"is ", u"foo"])
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes,
         Attributes("red", "default", set())],
        [screen.default_attributes] * 3,
        [screen.default_attributes] * 3
    ]

    # b) now inserting from the middle of the line
    screen.y, screen.x = 2, 1
    screen.insert_characters(1)
    assert screen.display == _([u"  s", u"is ", u"f o"])

    # c) inserting more than we have
    screen.insert_characters(10)
    assert screen.display == _([u"  s", u"is ", u"f  "])

    # d) 0 is 1
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]
    screen.cursor_position()
    screen.insert_characters()
    assert screen.display == _([u" sa", u"is ", u"foo"])
    assert screen.attributes == [
        [screen.default_attributes,
         Attributes("red", "default", set()),
         Attributes("red", "default", set())],
        [screen.default_attributes] * 3,
        [screen.default_attributes] * 3
    ]

    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]
    screen.cursor_position()
    screen.insert_characters(0)
    assert screen.display == _([u" sa", u"is ", u"foo"])
    assert screen.attributes == [
        [screen.default_attributes,
         Attributes("red", "default", set()),
         Attributes("red", "default", set())],
        [screen.default_attributes] * 3,
        [screen.default_attributes] * 3
    ]



def test_delete_characters():
    screen = Screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]

    screen.delete_characters(2)
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"m  ", u"is ", u"foo"])
    assert screen.attributes == [
        [Attributes("red", "default", set()),
         screen.default_attributes,
         screen.default_attributes],
        [screen.default_attributes] * 3,
        [screen.default_attributes] * 3
    ]

    screen.y, screen.x = 2, 2
    screen.delete_characters()
    assert screen.cursor == (2, 2)
    assert screen.display == _([u"m  ", u"is ", u"fo "])

    screen.y, screen.x = 1, 1
    screen.delete_characters(0)
    assert screen.cursor == (1, 1)
    assert screen.display == _([u"m  ", u"i  ", u"fo "])


    # ! extreme cases.
    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.x = 1
    screen.delete_characters(3)
    assert screen.cursor == (1, 0)
    assert screen.display == _([u"15   "])
    assert screen.attributes == [[
        Attributes("red", "default", set()),
        Attributes("red", "default", set()),
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes

    ]]

    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.x = 2
    screen.delete_characters(10)
    assert screen.cursor == (2, 0)
    assert screen.display == _([u"12   "])
    assert screen.attributes == [[
        Attributes("red", "default", set()),
        Attributes("red", "default", set()),
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes
    ]]

    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.delete_characters(4)
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"5    "])
    assert screen.attributes == [[
        Attributes("red", "default", set()),
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes
    ]]


def test_erase_character():
    screen = Screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.attributes = [[Attributes("red", "default", set())] * 3,
                         [screen.default_attributes] * 3,
                         [screen.default_attributes] * 3]


    screen.erase_characters(2)
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"  m", u"is ", u"foo"])
    screen.attributes = [
        [screen.default_attributes,
         screen.default_attributes,
         Attributes("red", "default", set())],
        [screen.default_attributes] * 3,
        [screen.default_attributes] * 3
    ]

    screen.y, screen.x = 2, 2
    screen.erase_characters()
    assert screen.cursor == (2, 2)
    assert screen.display == _([u"  m", u"is ", u"fo "])

    screen.y, screen.x = 1, 1
    screen.erase_characters(0)
    assert screen.cursor == (1, 1)
    assert screen.display == _([u"  m", u"i  ", u"fo "])

    # ! extreme cases.
    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.x = 1
    screen.erase_characters(3)
    assert screen.cursor == (1, 0)
    assert screen.display == _([u"1   5"])
    assert screen.attributes == [[
        Attributes("red", "default", set()),
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes,
        Attributes("red", "default", set())
    ]]

    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.x = 2
    screen.erase_characters(10)
    assert screen.cursor == (2, 0)
    assert screen.display == _([u"12   "])
    assert screen.attributes == [[
        Attributes("red", "default", set()),
        Attributes("red", "default", set()),
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes
    ]]

    screen = Screen(5, 1)
    screen.display = _(["12345"])
    screen.attributes = [[Attributes("red", "default", set())] * 5]
    screen.erase_characters(4)
    assert screen.cursor == (0, 0)
    assert screen.display == _([u"    5"])
    assert screen.attributes == [[
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes,
        screen.default_attributes,
        Attributes("red", "default", set())
    ]]


def test_erase_in_line():
    screen = Screen(5, 5)
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.attributes = [[Attributes("red", "default", set())] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5]
    screen.cursor_position(1, 3)

    # a) erase from cursor to the end of line
    screen.erase_in_line(0)
    assert screen.cursor == (2, 0)
    assert screen.display == _([u"sa   ",
                                u"s foo",
                                u"but a",
                                u"re yo",
                                u"u?   "])
    assert screen.attributes == [
        [Attributes("red", "default", set()),
         Attributes("red", "default", set()),
         screen.default_attributes,
         screen.default_attributes,
         screen.default_attributes],
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5
    ]

    # b) erase from the beginning of the line to the cursor
    screen.display = _(["sam*i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.attributes = [[Attributes("red", "default", set())] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5]
    screen.erase_in_line(1)
    assert screen.cursor == (2, 0)
    assert screen.display == _([u"   *i",
                               u"s foo",
                               u"but a",
                               u"re yo",
                               u"u?   "])
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes,
         screen.default_attributes,
         Attributes("red", "default", set()),
         Attributes("red", "default", set())],
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5
    ]

    # c) erase the entire line
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.attributes = [[Attributes("red", "default", set())] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5]
    screen.erase_in_line(2)
    assert screen.cursor == (2, 0)
    assert screen.display == _([u"     ",
                                u"s foo",
                                u"but a",
                                u"re yo",
                                u"u?   "])
    assert screen.attributes == [
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5
    ]



def test_erase_in_display():
    screen = Screen(5, 5)
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.attributes = [[screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [Attributes("red", "default", set())] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5]
    screen.cursor_position(3, 3)

    # a) erase from cursor to the end of the display, including
    #    the cursor
    screen.erase_in_display(0)
    assert screen.cursor == (2, 2)
    assert screen.display == _([u"sam i",
                                u"s foo",
                                u"bu   ",
                                u"     ",
                                u"     "])
    assert screen.attributes == [
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [Attributes("red", "default", set()),
         Attributes("red", "default", set()),
         screen.default_attributes,
         screen.default_attributes,
         screen.default_attributes],
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5
    ]

    # b) erase from the beginning of the display to the cursor,
    #    including it
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.attributes = [[screen.default_attributes] * 5,
                         [screen.default_attributes] * 5,
                         [Attributes("red", "default", set())] * 5,
                         [screen.default_attributes] * 5,
                         [screen.default_attributes] * 5]
    screen.erase_in_display(1)
    assert screen.cursor == (2, 2)
    assert screen.display == _([u"     ",
                                u"     ",
                                u"    a",
                                u"re yo",
                                u"u?   "])
    assert screen.attributes == [
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5,
        [screen.default_attributes,
         screen.default_attributes,
         screen.default_attributes,
         Attributes("red", "default", set()),
         Attributes("red", "default", set())],
        [screen.default_attributes] * 5,
        [screen.default_attributes] * 5
    ]

    # c) erase the while display
    screen.erase_in_display(2)
    assert screen.cursor == (2, 2)
    assert screen.display == _([u"     ",
                                u"     ",
                                u"     ",
                                u"     ",
                                u"     "])
    assert screen.attributes == [[screen.default_attributes] * 5] * 5


def test_cursor_up():
    screen = Screen(10, 10)

    # Moving the cursor up at the top doesn't do anything
    screen.cursor_up(1)
    assert screen.y == 0

    screen.y = 1

    # Moving the cursor past the top moves it to the top
    screen.cursor_up(10)
    assert screen.y == 0

    screen.y = 5
    # Can move the cursor more than one up.
    screen.cursor_up(3)
    assert screen.y == 2


def test_cursor_down():
    screen = Screen(10, 10)

    # Moving the cursor down at the bottom doesn't do anything
    screen.y = 9
    screen.cursor_down(1)
    assert screen.y == 9

    screen.y = 8

    # Moving the cursor past the bottom moves it to the bottom
    screen.cursor_down(10)
    assert screen.y == 9

    screen.y = 5
    # Can move the cursor more than one down.
    screen.cursor_down(3)
    assert screen.y == 8


def test_cursor_back():
    screen = Screen(10, 10)

    # Moving the cursor left at the margin doesn't do anything
    screen.x = 0
    screen.cursor_back(1)
    assert screen.x == 0

    screen.x = 3

    # Moving the cursor past the left margin moves it to the left margin
    screen.cursor_back(10)
    assert screen.x == 0

    screen.x = 5
    # Can move the cursor more than one back.
    screen.cursor_back(3)
    assert screen.x == 2


def test_cursor_forward():
    screen = Screen(10, 10)

    # Moving the cursor right at the margin doesn't do anything
    screen.x = 9
    screen.cursor_forward(1)
    assert screen.x == 9

    # Moving the cursor past the right margin moves it to the right margin
    screen.x = 8
    screen.cursor_forward(10)
    assert screen.x == 9

    # Can move the cursor more than one forward.
    screen.x = 5
    screen.cursor_forward(3)
    assert screen.x == 8


def test_cursor_position():
    screen = Screen(10, 10)

    # a) testing that we expect 1-indexed values
    screen.cursor_position(5, 10)
    assert screen.cursor == (9, 4)

    # b) but (0, 0) is also accepted and should be the same as (1, 1)
    screen.cursor_position(0, 10)
    assert screen.cursor == (9, 0)

    # c) moving outside the margins constrains to within the screen
    #    bounds
    screen.cursor_position(100, 5)
    assert screen.cursor == (4, 9)

    screen.cursor_position(5, 100)
    assert screen.cursor == (9, 4)

    # d) DECOM on
    screen.set_margins(5, 9)
    screen.set_mode(mo.DECOM)
    screen.cursor_position()
    assert screen.cursor == (0, 4)

    screen.cursor_position(2, 0)
    assert screen.cursor == (0, 5)

    # Note that cursor position doesn't change.
    screen.cursor_position(10, 0)
    assert screen.cursor == (0, 5)


def test_resize_shifts_vertical():
    # If the current display is shorter than the requested screen size...
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    # New rows should get added on the bottom...
    screen.resize(3, 2)

    assert repr(screen) == repr([u"bo", u"sh", u"  "])

    # If the current display is taller than the requested screen size...
    screen = Screen(2, 2)
    screen.display = _(["bo", "sh"])
    # Rows should be removed from the top...
    screen.resize(1, 2)

    assert repr(screen) == repr([u"sh"])


def test_unicode():
    stream = Stream()
    screen = Screen(4, 2)
    screen.attach(stream)

    try:
        stream.feed(u"тест")
    except UnicodeDecodeError:
        pytest.fail("Check your code -- we do accept unicode.")

    assert repr(screen) == repr([u"тест", u"    "])


def test_alignment_display():
    screen = Screen(5, 5)
    screen.draw(u"a")
    screen.linefeed()
    screen.linefeed()
    screen.draw(u"b")

    assert repr(screen) == repr([u"a    ",
                                 u"     ",
                                 u"b    ",
                                 u"     ",
                                 u"     "])

    screen.alignment_display()

    assert repr(screen) == repr([u"EEEEE",
                                 u"EEEEE",
                                 u"EEEEE",
                                 u"EEEEE",
                                 u"EEEEE"])

def test_set_margins():
    screen = Screen(10, 10)

    assert screen.margins == (0, 9)

    # a) ok-case
    screen.set_margins(1, 5)
    assert screen.margins == (0, 4)

    # b) one of the margins is out of bounds
    screen.set_margins(100, 10)
    assert screen.margins != (99, 9)
    assert screen.margins == (0, 4)

    # c) no margins provided
    screen.set_margins()
    assert screen.margins != (None, None)
    assert screen.margins == (0, 4)
