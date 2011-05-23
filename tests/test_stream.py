# -*- coding: utf-8 -*-

import pytest

import vt102
import vt102.control as ctrl, vt102.escape as esc


class counter(object):
    def __init__(self):
        self.count = 0

    def __call__(self, *args):
        self.count += 1


class argcheck(counter):
    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super(argcheck, self).__call__()


class argstore(object):
    def __init__(self):
        self.seen = []

    def __call__(self, *args):
        self.seen.extend(args)


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
        stream.feed(ctrl.CSI + u"6;Z")
    except Exception as e:
        pytest.fail("No exception should've raised, got: %s" % e)
    else:
        assert handler.count == 1
        assert handler.args == (ctrl.CSI + u"6;0Z", )


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
    assert handler.kwargs == {"private": True}

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


def test_missing_params():
    handler = argcheck()
    stream = vt102.Stream()
    stream.connect("cursor-position", handler)

    stream.feed(ctrl.CSI + u";" + esc.HVP)
    assert handler.count == 1
    assert handler.args == (0, 0)


def test_overflow():
    handler = argcheck()
    stream = vt102.Stream()
    stream.connect("cursor-position", handler)

    stream.feed(ctrl.CSI + u"999999999999999;99999999999999" + esc.HVP)
    assert handler.count == 1
    assert handler.args == (9999, 9999)


def test_interrupt():
    bugger, handler = argstore(), argcheck()
    stream = vt102.Stream()
    stream.connect("draw", bugger)
    stream.connect("cursor-position", handler)

    stream.feed(ctrl.CSI + u"10;" + ctrl.SUB + "10" + esc.HVP)

    assert not handler.count
    assert bugger.seen == [
        ctrl.SUB, "1", "0", esc.HVP
    ]


def test_control_characters():
    handler = argcheck()
    stream = vt102.Stream()
    stream.connect("cursor-position", handler)

    stream.feed(ctrl.CSI + u"10;\t\t\n\r\n10" + esc.HVP)

    assert handler.count == 1
    assert handler.args == (10, 10)

