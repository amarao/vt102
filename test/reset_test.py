#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import posix
import vt102
import fcntl
import sys
import os
import time

#those codes are sent by tset (reset) command for different type of terminals. Whe shall at least not crash on any of them.

seq_set={
"xterm":"\x1b[3g        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bHLF \x1bc\x1b[!p\x1b[?3;4l\x1b[4l\x1b>",

"vt102": "\x1b[3g        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bHLF \x1b>\x1b[?3l\x1b[?4l\x1b[?5l\x1b[?7h\x1b[?8h ",

"linux": "\x1b[3g        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bH        \x1bHLF \x1bc\x1b]R"
}

screen=vt102.screen((25,80))
stream=vt102.stream()
screen.attach(stream)
for seq in seq_set.itervalues():
    sream.process(seq)

for line in screen.display:
    print repr(line)
