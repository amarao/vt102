# -*- coding: utf-8 -*-

import pytest

import vt102
import vt102.control as ctrl


class counter(object):
    def __init__(self):
        self.count = 0

    def __call__(self, *args):
        self.count += 1


class argcheck(counter):
    def __call__(self, *args):
        self.args = args
        super(argcheck, self).__call__()


def test_basic_sequences():
    stream = vt102.Stream()

    for cmd, event in stream.escape.iteritems():
        handler = counter()
        stream.connect(event, handler)

        stream.consume(ctrl.ESC)
        assert stream.state == "escape"

        stream.consume(cmd)
        assert handler.count == 1
        assert stream.state == "stream"

    # ``linefeed``s is somewhat an exception, there's three ways to
    # trigger it.
    handler = counter()

    stream.connect("linefeed", handler)
    stream.feed(ctrl.LF + ctrl.VT + ctrl.FF)

    assert handler.count == 3
    assert stream.state == "stream"


def test_unknown_sequences():
    handler = argcheck()
    stream = vt102.Stream()
    stream.connect("debug", handler)

    try:
        stream.feed(u"\00" + ctrl.ESC + u"[6;7!")
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)
    else:
        assert handler.count == 1
        assert handler.args == (ctrl.CSI + u"6;7!", )


def test_non_csi_sequences():
    stream = vt102.Stream()

    for cmd, event in stream.csi.iteritems():
        # a) single param
        handler = argcheck()
        stream.connect(event, handler)
        stream.consume(ctrl.ESC)
        assert stream.state == "escape"

        stream.consume(u"[")
        assert stream.state == "arguments"

        stream.consume(u"5")
        stream.consume(cmd)

        assert handler.count == 1
        assert handler.args == (5, )
        assert stream.state == "stream"

        # b) multiple params, and starts with CSI, not ESC [
        handler = argcheck()
        stream.connect(event, handler)
        stream.consume(ctrl.CSI)
        assert stream.state == "arguments"

        stream.consume(u"5")
        stream.consume(u";")
        stream.consume(u"12")
        stream.consume(cmd)

        assert handler.count == 1
        assert handler.args == (5, 12)
        assert stream.state == "stream"


def test_mode_csi_sequences():
    bugger = counter()
    stream = vt102.Stream()
    stream.connect("debug", bugger)

    # a) set-mode
    handler = argcheck()
    stream.connect("set-mode", handler)
    stream.feed(ctrl.CSI + "?9;2h")

    assert not bugger.count
    assert handler.count == 1
    assert handler.args == (9, 2)

    # a) reset-mode
    handler = argcheck()
    stream.connect("reset-mode", handler)
    stream.feed(ctrl.CSI + "?9;2l")

    assert not bugger.count
    assert handler.count == 1
    assert handler.args == (9, 2)


def test_byte_stream():
    def validator(char):
        assert u"\uFFFD" not in char

    stream = vt102.ByteStream("utf-8")
    stream.connect("draw", validator)

    bytes = u"Garðabær".encode("utf-8")

    for byte in bytes:
        stream.feed(byte)

