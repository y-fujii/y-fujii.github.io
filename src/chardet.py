# Simple encoding detector compatible with chardet
# public domain

encodings = [
	"ascii",
	"utf-8",
	"euc-jp",
	"cp932",
	"iso-2022-jp",
]


def detect( text ):
	bestScore = -1
	bestEnc = None
	for enc in encodings:
		try:
			unicode( text, enc )
		except UnicodeDecodeError, err:
			if err.end > bestScore:
				bestScore = err.end
				bestEnc = enc
		else:
			return {
				"encoding": enc,
				"confidence": 1.0,
			}

	return {
		"encoding": bestEnc,
		"confidence": bestScore / (bestScore + 2.0),
	}
