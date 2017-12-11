# public domain

import sys
import re
import wave
import glob
import numarray

def write_wavefile(fn, data):
	wav = wave.open(fn, "w")
	wav.setnchannels(2)
	wav.setsampwidth(2)
	wav.setframerate(44100)
	wav.writeframes(data.tostring())
	wav.close()

for fn in glob.glob("elev*/*.dat"):
	src = numarray.fromfile(fn, numarray.Int16)
	if sys.byteorder == "little":
		src.byteswap()

	(pre, ang) = re.match("(elev-?\d+/H-?\d+e)(\d+)a.dat", fn).groups()
	ang = int(ang)
	write_wavefile("%s%03da.wav" % (pre, ang), src)

	if ang != 0 and ang != 180:
		tmp = numarray.array(type=numarray.Int16, shape=src.shape)
		tmp[0::2] = src[1::2]
		tmp[1::2] = src[0::2]
		write_wavefile("%s%03da.wav" % (pre, 360 - ang), tmp)
