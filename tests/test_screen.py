# -*- coding: utf-8 -*-

from __future__ import print_function

from array import array

import pytest

import vt102
import vt102.modes as mo

# A shortcut, which converts an iterable yielding byte strings
# to a list of arrays in "utf-8".
_ = lambda lines: [array("u", l.decode("utf-8")) for l in lines]


def test_remove_non_existant_attribute():
    screen = vt102.screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.remove_text_attr("underline")
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2


def test_attributes():
    screen = vt102.screen(2, 2)
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
    assert screen.cursor_attributes == (("bold",), "default", "default")

    screen.print(u"f")
    assert screen.attributes == [
        [(("bold",), "default", "default"), screen.default_attributes],
        [screen.default_attributes, screen.default_attributes]
    ]


def test_colors():
    screen = vt102.screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.select_graphic_rendition(30) # black foreground
    screen.select_graphic_rendition(40) # black background
    assert screen.cursor_attributes == ((), "black", "black")

    screen.select_graphic_rendition(31) # red foreground
    assert screen.cursor_attributes == ((), "red", "black")


def test_reset_resets_colors():
    screen = vt102.screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2

    screen.select_graphic_rendition(30) # black foreground
    screen.select_graphic_rendition(40) # black background
    assert screen.cursor_attributes == ((), "black", "black")

    screen.select_graphic_rendition(0)
    assert screen.cursor_attributes == screen.default_attributes


def test_multi_attribs():
    screen = vt102.screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    screen.select_graphic_rendition(1) # Bold
    screen.select_graphic_rendition(5) # Blinke

    assert screen.cursor_attributes == (("bold", "blink"), "default", "default")


def test_attributes_reset():
    screen = vt102.screen(2, 2)
    assert screen.attributes == [
        [screen.default_attributes,
         screen.default_attributes]
    ] * 2
    screen.select_graphic_rendition(1) # Bold
    screen.print(u"f")
    screen.print(u"o")
    screen.print(u"o")
    assert screen.attributes == [
        [(("bold",), "default", "default"),
         (("bold",), "default", "default")],
        [(("bold",), "default", "default"), screen.default_attributes],
    ]

    screen.home()
    screen.select_graphic_rendition(0) # Reset
    screen.print(u"f")
    assert screen.attributes == [
        [screen.default_attributes, (("bold",), "default", "default")],
        [(("bold",), "default", "default"), screen.default_attributes],
    ]


def test_resize():
    screen = vt102.screen(2, 2)
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


def test_print():
    # ``DECAWM`` on (default).
    screen = vt102.screen(3, 3)
    assert mo.DECAWM in screen.mode

    map(screen.print, u"abc")
    assert repr(screen) == repr([u"abc", u"   ", u"   "])
    assert screen.cursor == (3, 0)

    # ... one` more character -- now we got a linefeed!
    screen.print(u"a")
    assert screen.cursor == (1, 1)

    # ``DECAWM`` is off.
    screen = vt102.screen(3, 3)
    screen.reset_mode(mo.DECAWM)

    map(screen.print, u"abc")
    assert repr(screen) == repr([u"abc", u"   ", u"   "])
    assert screen.cursor == (3, 0)

    # No linefeed is issued on the end of the line ...
    screen.print(u"a")
    assert repr(screen) == repr([u"aba", u"   ", u"   "])
    assert screen.cursor == (3, 0)


def test_carriage_return():
    screen = vt102.screen(3, 3)
    screen.x = 2
    screen.carriage_return()

    assert screen.x == 0


def test_index():
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])

    # a) indexing on a row that isn't the last should just move
    # the cursor down.
    screen.index()
    assert screen.cursor == (0, 1)

    # b) indexing on the last row should push everything up and
    # create a new row at the bottom.
    screen.index()
    assert repr(screen) == repr([u"sh", u"  "])
    assert screen.y == 1

    # c) same with margins
    screen = vt102.screen(5, 2)
    screen.display = _(["bo", "sh", "th", "er", "oh"])
    screen.set_margins(2, 4)
    screen.y = 3

    # ... go!
    screen.index()
    assert repr(screen) == repr([u"bo", u"th", u"er", u"  ", u"oh"])
    assert screen.cursor == (0, 3)

    # ... and again ...
    screen.index()
    assert repr(screen) == repr([u"bo", u"er", u"  ", u"  ", u"oh"])
    assert screen.cursor == (0, 3)

    # ... and again ...
    screen.index()
    assert repr(screen) == repr([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.cursor == (0, 3)

    # look, nothing happens!
    screen.index()
    assert repr(screen) == repr([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.cursor == (0, 3)


def test_reverse_index():
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])

    # a) reverse indexing on the first row should push rows down
    # and create a new row at the top.
    screen.reverse_index()
    assert screen.cursor == (0, 0)
    assert repr(screen) == repr([u"  ", u"bo"])

    # b) once again ...
    screen.y = 1
    screen.reverse_index()

    assert repr(screen) == repr([u"  ", u"bo"])
    assert screen.cursor == (0, 0)

    # c) same with margins
    screen = vt102.screen(5, 2)
    screen.display = _(["bo", "sh", "th", "er", "oh"])
    screen.set_margins(2, 4)
    screen.y = 1

    # ... go!
    screen.reverse_index()
    assert repr(screen) == repr([u"bo", u"  ", u"sh", u"th", u"oh"])
    assert screen.cursor == (0, 1)

    # ... and again ...
    screen.reverse_index()
    assert repr(screen) == repr([u"bo", u"  ", u"  ", u"sh", u"oh"])
    assert screen.cursor == (0, 1)

    # ... and again ...
    screen.reverse_index()
    assert repr(screen) == repr([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.cursor == (0, 1)

    # look, nothing happens!
    screen.reverse_index()
    assert repr(screen) == repr([u"bo", u"  ", u"  ", u"  ", u"oh"])
    assert screen.cursor == (0, 1)


def test_linefeed():
    screen = vt102.screen(2, 2)
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
    screen = vt102.screen(10, 10)

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
    screen = vt102.screen(10, 10)
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
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])
    # New columns should get added to the right.
    screen.resize(2, 3)

    assert repr(screen) == repr([u"bo ", u"sh "])

    # If the current display is wider than the requested size...
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])
    # Columns should be removed from the right...
    screen.resize(2, 1)

    assert repr(screen) == repr([u"b", u"s"])


def test_backspace():
    screen = vt102.screen(2, 2)
    assert screen.x == 0
    screen.backspace()
    assert screen.x == 0
    screen.x = 1
    screen.backspace()
    assert screen.x == 0


def test_save_cursor():
    screen = vt102.screen(10, 10)
    screen.save_cursor()

    screen.x = 3
    screen.y = 5
    screen.save_cursor()
    screen.x = 4
    screen.y = 4
    screen.restore_cursor()

    assert screen.x == 3
    assert screen.y == 5

    screen.restore_cursor()

    assert screen.x == 0
    assert screen.y == 0


def test_restore_cursor_with_none_saved():
    screen = vt102.screen(10, 10)
    screen.x = 5
    screen.y = 5
    screen.restore_cursor()

    assert screen.cursor == (0, 0)


def test_insert_lines():
    # a) without margins
    screen = vt102.screen(3, 3)
    assert screen.cursor == (0, 0)

    screen.display = _(["sam", "is ", "foo"])
    screen.insert_lines()

    assert repr(screen) == repr([u"   ", u"sam", u"is "])
    assert screen.cursor == (0, 0)

    screen.display = _(["sam", "is ", "foo"])
    screen.insert_lines(2)

    assert repr(screen) == repr([u"   ", u"   ", u"sam"])

    # b) with margins
    screen = vt102.screen(5, 3)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.set_margins(1, 4)
    screen.y = 1
    screen.insert_lines(1)

    assert repr(screen) == repr([u"sam", u"   ", u"is ", u"foo", u"baz"])

    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.set_margins(1, 3)
    screen.y = 1

    screen.insert_lines(1)
    assert repr(screen) == repr([u"sam", u"   ", u"is ", u"bar",  u"baz"])

    screen.insert_lines(2)
    assert repr(screen) == repr([u"sam", u"   ", u"   ", u"bar",  u"baz"])

    # c) with margins -- trying to insert more than we have available
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.set_margins(2, 4)
    screen.y = 1
    screen.insert_lines(20)

    assert repr(screen) == repr([u"sam", u"   ", u"   ", u"   ", u"baz"])

    # d) with margins -- trying to insert outside scroll boundaries
    screen = vt102.screen(5, 3)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.set_margins(2, 4)
    screen.insert_lines(5)

    assert repr(screen) == repr([u"sam", u"is ", u"foo", u"bar", u"baz"])


def test_delete_lines():
    # a) without margins
    screen = vt102.screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])
    screen.delete_lines()

    assert repr(screen) == repr([u"is ", u"foo", u"   "])
    assert screen.cursor == (0, 0)

    screen.delete_lines(0)

    assert repr(screen) == repr([u"foo", u"   ", u"   "])
    assert screen.cursor == (0, 0)

    # b) with margins
    screen = vt102.screen(5, 3)
    screen.set_margins(1, 4)
    screen.y = 1

    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.delete_lines(1)
    assert repr(screen) == repr([u"sam", u"foo", u"bar", u"   ", u"baz"])

    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.delete_lines(2)
    assert repr(screen) == repr([u"sam", u"bar", u"   ", u"   ", u"baz"])

    # c) with margins -- trying to delete  more than we have available
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.delete_lines(5)
    assert repr(screen) == repr([u"sam", u"   ", u"   ", u"   ", u"baz"])

    # d) with margins -- trying to delete outside scroll boundaries
    screen = vt102.screen(5, 3)
    screen.display = _(["sam", "is ", "foo", "bar", "baz"])
    screen.set_margins(2, 4)
    screen.delete_lines(5)

    assert repr(screen) == repr([u"sam", u"is ", u"foo", u"bar", u"baz"])


def test_insert_characters():
    screen = vt102.screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])

    # a) normal case
    cursor = screen.cursor
    screen.insert_characters(2)
    assert repr(screen) == repr([u"  s", u"is ", u"foo"])
    assert screen.cursor == cursor

    # b) now inserting from the middle of the line
    screen.y, screen.x = 2, 1
    screen.insert_characters(1)
    assert repr(screen) == repr([u"  s", u"is ", u"f o"])

    # c) inserting more than we have
    screen.insert_characters(10)
    assert repr(screen) == repr([u"  s", u"is ", u"f  "])

    # d) 0 is 1
    screen.display = _(["sam", "is ", "foo"])
    screen.home()
    screen.insert_characters()
    assert repr(screen) == repr([u" sa", u"is ", u"foo"])

    screen.display = _(["sam", "is ", "foo"])
    screen.home()
    screen.insert_characters(0)
    assert repr(screen) == repr([u" sa", u"is ", u"foo"])


def test_delete_characters():
    screen = vt102.screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])

    screen.delete_characters(2)
    assert repr(screen) == repr([u"m  ", u"is ", u"foo"])

    screen.y, screen.x = 2, 2
    screen.delete_characters()
    assert repr(screen) == repr([u"m  ", u"is ", u"fo "])

    screen.y, screen.x = 1, 1
    screen.delete_characters(0)
    assert repr(screen) == repr([u"m  ", u"i  ", u"fo "])


    # ! extreme cases.
    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.x = 1
    screen.delete_characters(3)
    assert repr(screen) == repr([u"15   "])

    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.x = 2
    screen.delete_characters(10)
    assert repr(screen) == repr([u"12   "])

    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.delete_characters(4)
    assert repr(screen) == repr([u"5    "])


def test_erase_character():
    screen = vt102.screen(3, 3)
    screen.display = _(["sam", "is ", "foo"])

    screen.erase_characters(2)
    assert repr(screen) == repr([u"  m", u"is ", u"foo"])

    screen.y, screen.x = 2, 2
    screen.erase_characters()
    assert repr(screen) == repr([u"  m", u"is ", u"fo "])

    screen.y, screen.x = 1, 1
    screen.erase_characters(0)
    assert repr(screen) == repr([u"  m", u"i  ", u"fo "])

    # ! extreme cases.
    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.x = 1
    screen.erase_characters(3)
    assert repr(screen) == repr([u"1   5"])

    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.x = 2
    screen.erase_characters(10)
    assert repr(screen) == repr([u"12   "])

    screen = vt102.screen(1, 5)
    screen.display = _(["12345"])
    screen.erase_characters(4)
    assert repr(screen) == repr([u"    5"])


def test_erase_in_line():
    screen = vt102.screen(5, 5)
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.cursor_position(1, 3)

    # Erase from cursor to the end of line
    screen.erase_in_line(0)
    assert repr(screen) == repr([u"sa   ",
                                 u"s foo",
                                 u"but a",
                                 u"re yo",
                                 u"u?   "])

    # Erase from the beginning of the line to the cursor
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.erase_in_line(1)
    assert repr(screen) == repr([u"    i",
                                 u"s foo",
                                 u"but a",
                                 u"re yo",
                                 u"u?   "])

    screen.y = 1
    # Erase the entire line
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.erase_in_line(2)
    assert repr(screen) == repr([u"sam i",
                                 u"     ",
                                 u"but a",
                                 u"re yo",
                                 u"u?   "])


def test_erase_in_display():
    screen = vt102.screen(5, 5)
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.cursor_position(3, 3)

    # Erase from the cursor to the end of the display.
    screen.erase_in_display(0)
    assert repr(screen) == repr([u"sam i",
                                 u"s foo",
                                 u"bu   ",
                                 u"     ",
                                 u"     "])
    assert screen.attributes == [[screen.default_attributes] * 5] * 5

    # Erase from cursor to the beginning of the display.
    screen.display = _(["sam i",
                        "s foo",
                        "but a",
                        "re yo",
                        "u?   "])
    screen.erase_in_display(1)
    assert repr(screen) == repr([u"     ",
                                 u"     ",
                                 u"    a",
                                 u"re yo",
                                 u"u?   "])
    assert screen.attributes == [[screen.default_attributes] * 5] * 5

    screen.y = 1
    # Erase the entire screen
    screen.erase_in_display(2)
    assert repr(screen) == repr([u"     ",
                                 u"     ",
                                 u"     ",
                                 u"     ",
                                 u"     "])
    assert screen.attributes == [[screen.default_attributes] * 5] * 5


def test_cursor_up():
    screen = vt102.screen(10, 10)

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
    screen = vt102.screen(10, 10)

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
    screen = vt102.screen(10, 10)

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
    screen = vt102.screen(10, 10)

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
    screen = vt102.screen(10, 10)

    # Note, that rows / columns are backwards of x / y and are 1-indexed
    # instead of 0-indexed.
    screen.cursor_position(5, 10)
    assert screen.cursor == (9, 4)

    # Confusingly enough, however, 0-inputs are acceptable and should be
    # the same a 1.
    screen.cursor_position(0, 10)
    assert screen.cursor == (9, 0)

    # Moving outside the margins constrains to within the marginscreen.
    screen.cursor_position(100, 5)
    assert screen.cursor == (4, 9)

    screen.cursor_position(5, 100)
    assert screen.cursor == (9, 4)


def test_home():
    screen = vt102.screen(10, 10)
    screen.x, screen.y = 5, 5
    screen.home()

    assert screen.cursor == (0, 0)


def test_resize_shifts_vertical():
    # If the current display is shorter than the requested screen size...
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])
    # New rows should get added on the bottom...
    screen.resize(3, 2)

    assert repr(screen) == repr([u"bo", u"sh", u"  "])

    # If the current display is taller than the requested screen size...
    screen = vt102.screen(2, 2)
    screen.display = _(["bo", "sh"])
    # Rows should be removed from the top...
    screen.resize(1, 2)

    assert repr(screen) == repr([u"sh"])


def test_unicode():
    stream = vt102.stream()
    screen = vt102.screen(2, 4)
    screen.attach(stream)

    try:
        stream.feed(u"тест")
    except UnicodeDecodeError:
        pytest.fail("Check your code -- we do accept unicode.")

    assert repr(screen) == repr([u"тест", u"    "])


def test_alignment_display():
    screen = vt102.screen(5, 5)
    screen.print(u"a")
    screen.linefeed()
    screen.linefeed()
    screen.print(u"b")

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
    screen = vt102.screen(10, 10)

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
