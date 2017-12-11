# public domain

import sys
import re
import wave
import glob
import numarray


max_val = 0
for fn in glob.glob("elev*/*.dat"):
	src = numarray.fromfile(fn, numarray.Float32)
	if sys.byteorder == "little":
		src.byteswap()
	
	max_val = max(max_val, abs(src.max()))


for fn in glob.glob("elev*/*L*.dat"):
	L = numarray.fromfile(fn, numarray.Float32)
	R = numarray.fromfile(fn.replace("L", "R"), numarray.Float32)
	if sys.byteorder == "little":
		L.byteswap()
		R.byteswap()

	dst = numarray.array(type=numarray.Int16, shape=[L.shape[0] * 2])
	dst[0::2] = L * 32767 / max_val
	dst[1::2] = R * 32767 / max_val

	wav = wave.open(fn.replace("L", "").replace(".dat", ".wav"), "w")
	wav.setnchannels(2)
	wav.setsampwidth(2)
	wav.setframerate(44100)
	wav.writeframes(dst.tostring())
	wav.close()
