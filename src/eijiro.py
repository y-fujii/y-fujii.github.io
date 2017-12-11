#!/usr/bin/env python
# public domain

import re
import os
import urllib
import urllib2
import threading
import codecs
import Tkinter
import ScrolledText
import socket

socket.setdefaulttimeout(4)

tkStyle = {
	"bg": "white",
	"spacing1": 8,
	#"font": "",
}


def search(word, count):
	param = urllib.urlencode({
		"word_in": word.encode("shift-jis"),
		"word_in3": "x",
		"cnt_stp": str(count * 50),
	})
	html = urllib2.urlopen(urllib2.Request(
		"http://www2.alc.co.jp/ejr/index.php?" + param,
		None,
		{"User-Agent": "Mozilla/5.0"},
	))
	(w3mOut, w3mIn) = os.popen2("w3m -e -dump -T text/html -cols 80")

	def dumpThread(html=html, w3mIn=w3mIn):
		try:
			for line in html:
				if line.strip() == "<ul>":
					w3mOut.write(line)
					break

			for line in html:
				w3mOut.write(line)
				if line.strip() == "</ul>":
					break
		finally:
			w3mOut.close()
			html.close()

	t = threading.Thread(target=dumpThread)
	t.start()

	retv = codecs.getreader("euc-jp")(w3mIn).read()

	t.join()
	return retv


class App:
	def __init__(self):
		self.interval = 500
		self.word = u""
		self.tk = Tkinter.Tk()
		self.tk.resizable(0, 1)
		self.tkText = ScrolledText.ScrolledText(self.tk, width=70, **tkStyle)
		self.tkText.pack(expand=1, fill=Tkinter.BOTH)
		self.tk.after(self.interval, self.onTime)
		self.tk.mainloop()


	def onTime(self):
		try:
			word = unicode(self.tk.selection_get(selection="PRIMARY"))
			word = re.sub("[^a-zA-Z]", " ", word)
			word = re.sub("[ \t\n]+", " ", word)
			word = word.strip()
		except Tkinter.TclError:
			word = u""

		if word != u"" and word != self.word:
			self.word = word
			self.tkText.delete("0.0", Tkinter.END)
			try:
				text = search(word, 0)
				self.tkText.insert(Tkinter.END, text)
			except urllib2.URLError:
				self.tkText.insert(Tkinter.END, "failed.")

		self.tk.after(self.interval, self.onTime)


if __name__ == "__main__":
	App()
