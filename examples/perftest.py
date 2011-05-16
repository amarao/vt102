#!/usr/bin/env python
import sys

sys.path.append("..")
import vt102
import time

"""
	performance test: print data to stream without rendering, displays
	speed during tests (Ctrl-C to interrupt)
"""

stream = vt102.Stream()
screen = vt102.Screen(80, 24)
screen.attach(stream)

while 1:
	begin=time.time()
	cnt=0
	while time.time()<begin+1:
		stream.feed(u"*")
		cnt+=1
	print "CPS ~=", cnt/(time.time()-begin)

