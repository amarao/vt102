# -*- coding: utf-8 -*-

import pytest

import vt102
import vt102.escape as esc
import vt102.control as ctrl


class counter(object):
    def __init__(self):
        self.count = 0

    def __call__(self, **args):
        self.count += 1


class argcheck(counter):
    def __call__(self, *args):
        self.args = args
        super(argcheck, self).__call__()


def test_multi_param():
    stream = vt102.stream()
    stream.state = "escape-lb"
    stream.feed("5;25")

    assert stream.params == [5]
    assert stream.current_param == "25"


def test_cursor_down():
    handler = argcheck()
    stream = vt102.stream()
    stream.connect("cursor-down", handler)
    stream.feed("\000" + chr(ctrl.ESC) + "[5" + chr(esc.CUD))

    assert handler.count == 1
    assert handler.args == (5, )
    assert stream.state == "stream"


def test_cursor_up():
    handler = argcheck()
    stream = vt102.stream()
    stream.connect("cursor-up", handler)
    stream.feed(u"\000" + unichr(ctrl.ESC) + u"[5" + unichr(esc.CUU))

    assert handler.count == 1
    assert handler.args == (5, )
    assert stream.state == "stream"


def test_basic_escapes():
    stream = vt102.stream()

    for cmd, event in stream.escape.iteritems():
        handler = counter()
        stream.connect(event, handler)

        stream.consume(unichr(ctrl.ESC))
        assert stream.state == "escape"

        stream.consume(unichr(cmd))
        assert handler.count == 1
        assert stream.state == "stream"


def test_invalid_escapes():
    stream = vt102.stream()
    screen = vt102.screen(25, 80)
    screen.attach(stream)

    # Escape sequence, sent by `reset` (tset) command crashed vt102,
    # making sure it won't ever happen again :)
    # a) TERM=vt102
    try:
        stream.feed(
            u"\x1b[3g\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bHLF"
            u"\x1b>\x1b[?3l\x1b[?4l\x1b[?5l\x1b[?7h\x1b[?8h"
        )
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)

    # b) TERM=xterm
    try:
        stream.feed(
            u"\x1b[3g\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bHLF"
            u"\x1bc\x1b[!p\x1b[?3;4l\x1b[4l\x1b>"
        )
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)

    # c) TERM=linux
    try:
        stream.feed(
            u"\x1b[3g\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bH\x1bHLF"
            u"\x1bc\x1b]R"
        )
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)


def test_unknown_escapes():
    stream = vt102.stream()
    screen = vt102.screen(1, 20)
    screen.attach(stream)

    handler = argcheck()
    stream.connect("debug", handler)

    try:
        stream.feed(u"\000" + unichr(ctrl.ESC) + u"[6;7!")
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)
    else:
        assert handler.count == 1
        assert handler.args == (u"^[6;7!", )


def test_backspace():
    handler = counter()
    stream = vt102.stream()

    stream.connect("backspace", handler)
    stream.consume(unichr(ctrl.BS))

    assert handler.count == 1
    assert stream.state == "stream"


def test_tab():
    handler = counter()
    stream = vt102.stream()

    stream.connect("tab", handler)
    stream.consume(unichr(ctrl.HT))

    assert handler.count == 1
    assert stream.state == "stream"


def test_linefeed():
    handler = counter()
    stream = vt102.stream()

    stream.connect("linefeed", handler)
    stream.feed(unichr(ctrl.LF) + unichr(ctrl.VT) + unichr(ctrl.FF))

    assert handler.count == 3
    assert stream.state == "stream"


def test_carriage_return():
    handler = counter()
    stream = vt102.stream()

    stream.connect("carriage-return", handler)
    stream.consume(unichr(ctrl.CR))

    assert handler.count == 1
    assert stream.state == "stream"
