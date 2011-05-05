#!/usr/bin/env python
import vt102
import sys
import time

"""
	simple vt102 testing script
	usage: vt102 source_file [delay]
	source_file may be fifo or regular file
	delay in seconds (can be less than second)
	sample:
		./termdbg escape_test.txt 0.1
"""

input_file=file(sys.argv[1])

try:
	delay=float(sys.argv[2])
except:
	delay=0

stream = vt102.stream()
screen = vt102.screen(24, 80)
screen.attach(stream)

utf8_state=0
utf8_buff=[]
utf8_len_mask={
	0b11100000:(0b11000000,1),
	0b11110000:(0b11100000,2),
	0b11111100:(0b11111000,3),
	0b11111110:(0b11111100,4),
	0b11111111:(0b11111110,5)
}
byte_counter=0
char_counter=0
line_mark=0
print "\x1b7\x1b[2J"
while 1:
	byte=input_file.read(1)
	byte_counter+=1
	if not byte:
		print "Got EOF"
		break
	if utf8_state:
		if ord(byte)&0b11000000 == 0b10000000: #utf8 sequence
			utf8_buff.append(byte)
			utf8_state-=1
			if utf8_state:
				continue
			else:
				char = "".join(utf8_buff).decode("utf-8")
				utf8_buff=[]
				char_counter+=1
		else:
			char=str(ord(byte)).decode("utf-8")
			char_counter+=1
			utf8_state=0
	else:
		if ord(byte)>=128:
			for mask in utf8_len_mask.iteritems():
				if ord(byte) & mask[0]==mask[1][0]:
					utf8_state=mask[1][1]
					utf8_buff.append(byte)
					break
			else:
				char=u"?"
				char_counter+=1
				utf8_state=0
		else:
			char=byte.decode("utf-8")
			char_counter+=1	

	if utf8_state:
		continue

	stream.feed(char)

	print "\x1b[0;0H char_counter=",char_counter,"byte_counter=",byte_counter,"current char=",ord(char), "\x1b[K"
	print "  *"+"-*"*40 + "*"
	for num,line in enumerate(screen.display):
		if line_mark:
			print "\x1b[1m",
			line_mark=0
		else:
			print "\x1b[0;12m",
			line_mark=1

		print u"%2d"%num+"|"+line.tounicode()+"|"
	print "  *"+"-*"*40 + "*"
	print "delaying for", delay, " sec"
	time.sleep(delay)

print "\x1b[0;m\x1b8"

