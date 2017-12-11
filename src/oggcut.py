#!/usr/bin/env python
# Ogg container extractor
# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import os
import mmap
import struct
import optparse

try:
	import psyco
	psyco.full()
except:
	pass


def makeCRCTable( idx ):
	r = idx << 24
	for i in range( 8 ):
		if r & 0x80000000 != 0:
			r = ((r & 0x7fffffff) << 1) ^ 0x04c11db7
		else:
			r = ((r & 0x7fffffff) << 1)

	return r


CRCTable = [ makeCRCTable( i ) for i in range( 256 ) ]


def CRC( src ):
	crc = 0
	for c in src:
		crc = ((crc & 0xffffff) << 8) ^ CRCTable[(crc >> 24) ^ ord(c)]
	return crc


def dumpOgg( src, useCRC ):
	hdStruct = "<4sBBQIIIB"
	hdSize = struct.calcsize( hdStruct )

	ogg = {}
	i = 0
	while True:
		i = src.find( "OggS\x00", i ) # with version info
		if i < 0 or i + hdSize > len( src ):
			break

		(_, _, flag, _, id, page, crc, nTbl) = \
			struct.unpack( hdStruct, src[i : i + hdSize] )

		if i + hdSize + nTbl > len( src ):
			i += 5
			continue

		table = src[i + hdSize : i + hdSize + nTbl]
		size = hdSize + nTbl + sum( ord( e ) for e in table )

		if useCRC and crc != CRC( src[i:i+22] + "\x00\x00\x00\x00" + src[i+26:i+size] ):
			i += 5
			continue

		# flag & 0x02 != 0 and id not in ogg
		# flag & 0x02 == 0 and id in ogg

		if flag & 0x02 != 0 or id not in ogg:
			ogg[id] = []

		ogg[id] += [ (i, i + size) ]

		if flag & 0x04 != 0:
			yield "".join( src[bgn:end] for (bgn, end) in ogg[id] )
			del ogg[id]

		i += size


def main():
	optParser = optparse.OptionParser()
	optParser.add_option(
		"-c",
		action = "store_true",
		dest = "useCRC",
		help = "Enable CRC checking"
	)
	(opt, args) = optParser.parse_args()

	fileId = 0
	for arg in args:
		fd = os.open( arg, os.O_RDONLY )
		try:
			size = os.fstat( fd )[6]
			data = mmap.mmap( fd, size, access = mmap.ACCESS_READ )

			for ogg in dumpOgg( data, opt.useCRC ):
				fn = "%04d.ogg" % fileId
				print "%s: %dbytes" % (fn, len( ogg ))
				file( fn, "w" ).write( ogg )
				fileId += 1
		finally:
			os.close( fd )


if __name__ == "__main__":
	main()
