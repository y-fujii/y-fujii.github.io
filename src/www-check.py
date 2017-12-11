#!/usr/pkg/bin/python2.4
# encoding: euc-jp

import re
import os
import threading
import socket
import urllib2
from email import Utils
import cgi
import time
import pickle
import difflib


nParallel = 4
infoFile = os.environ["HOME"] + "/.www-info-1.1"
listFile = os.environ["HOME"] + "/.www-list"
htmlFile = os.environ["HOME"] + "/web/www-check.html"
browser = 'firefox -remote "openURL(file://%s, new-tab)"' % htmlFile

htmlHeader = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
	<head>
		<meta http-equiv="content-type" content="application/xhtml+xml; charset=euc-jp" />
		<title>www-checker</title>
		<style type="text/css">
			table {
				margin-left: auto;
				margin-right: auto;
				border-spacing: 0.5em;
			}

			td {
				vertical-align: top;
				white-space: nowrap;
			}

			pre {
				width: 40em;
				margin: 0.25em 0em;
				padding: 0.25em 0.5em;
				overflow: hidden;
				-moz-border-radius: 0.5em;
			}

			a {
				text-decoration: none;
			}

			a:hover {
				text-decoration: underline;
			}
		</style>
	</head>
	<body>

<table>
"""

htmlContent = """
<tr style="color: %(fg-color)s">
<td>%(yyyy)04d/%(mo)02d/%(dd)02d %(hh)02d:%(mi)02d</td>
<td>%(method)s</td>
<td>
<a href="%(url)s" style="color: %(url-color)s">%(title)s</a>
<pre style="background-color: %(bg-color)s">
%(summary)s
</pre>
</td>
</tr>
"""

htmlFooter = """
</table>
</body>
</html>
"""


def main():
	urls = file(listFile).read().splitlines()
	try:
		oldInfos = pickle.load(file(infoFile))
	except:
		oldInfos = []
	
	infoDic = dict( (t.url, t) for t in oldInfos )
	def f(url):
		if url in infoDic.keys():
			return infoDic[url]
		else:
			return URLInfo(url)
	newInfos = [ f(url) for url in urls ]

	socket.setdefaulttimeout(30)
	parallel([ t.update for t in newInfos ], nParallel)

	newInfos.sort(lambda x, y: cmp(x.date, y.date))
	newInfos.reverse()
	pickle.dump(newInfos, file(infoFile, "w"))

	outs = file(htmlFile, "w")
	outs.write(htmlHeader)
	for info in newInfos:
		def color(r, g, b):
			w = max(32 - info.ratio, 0)
			rr = r + w * (255 - r) / 64
			gg = g + w * (255 - g) / 64
			bb = b + w * (255 - b) / 64
			return '#%02x%02x%02x' % (rr, gg, bb)

		tm = time.localtime(info.date)
		summary = "\n".join([ t for t in info.diff if t.strip() != "" ][:4])
		outs.write(
			htmlContent % {
				"fg-color": color(0, 0, 0),
				"bg-color": color(240, 236, 224),
				"url-color": color(16, 128, 16),
				"yyyy": tm[0],
				"mo": tm[1],
				"dd": tm[2],
				"hh": tm[3],
				"mi": tm[4],
				"method": cgi.escape(info.method),
				"url": cgi.escape(info.url),
				"title": cgi.escape(info.title),
				"summary": cgi.escape(summary),
			}
		)

	outs.write(htmlFooter)
	outs.close()

	os.system(browser)


class URLInfo:
	def __init__(self, url):
		self.url = url
		self.text = []
		self.date = 0
		self.length = 0
		self.ratio = 0
		self.method = ""
		self.diff = []
		self.title = url


	def update(self):
		# XXX
		print self.url

		req = urllib2.Request(self.url, headers = {
			"if-modified-since": Utils.formatdate(self.date)
		})
		try:
			f = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			if err.code == 304:
				self.method = "If-modified-since"
				self.ratio = 0
				return
			else:
				self.method = "Error %d" % err.code
				return
		except urllib2.URLError:
			self.method = "Error URL"
			return
		except socket.timeout:
			self.method = "Error timeout"
			return

		if "last-modified" in f.info():
			date = Utils.mktime_tz(Utils.parsedate_tz(f.info()["last-modified"]))
			if date == self.date:
				self.method = "Last-modified"
				self.ratio = 0
				return
		else:
			date = time.time()

		if "content-length" in f.info():
			length = f.info()["content-length"]
			if length == self.length:
				self.method = "Content-length"
				self.ratio = 0
				return
			else:
				self.length = length

		try:
			html = f.read()
		except socket.timeout:
			self.method = "Error timeout"
			return
		f.close()

		(self.title, text) = html2text(html)
		if self.title.strip() == "":
			self.title = self.url

		(self.ratio, diff, count) = isUpdated(self.text, text)
		self.text = text
		self.method = "GET (%03d %03d %03d)" % count
		if self.ratio > 0:
			self.date = date
			self.diff = diff


def isUpdated(old, new):
	opcodes = difflib.SequenceMatcher(None, old, new).get_opcodes()

	#nIns = sum(j2 - j1 for (tag, i1, i2, j1, j2) in opcodes if tag != "equal")
	#nDel = sum(i2 - i1 for (tag, i1, i2, j1, j2) in opcodes if tag != "equal")
	#nRep = sum(i2 - i1 + j2 - j1 for (tag, i1, i2, j1, j2) in opcodes if tag == "replace")
	nIns = 0
	nDel = 0
	nRep = 0
	insText = []
	for (tag, i1, i2, j1, j2) in opcodes:
		li = i2 - i1
		lj = j2 - j1
		if tag == "delete":
			nDel += li
		elif tag == "insert":
			nIns += lj
			insText += new[j1:j2]
		elif tag == "replace":
			if -1 <= li - lj <= 1 and li + lj <= 6:
				nRep += li + lj
			else:
				nDel += li
				nIns += lj
				insText += new[j1:j2]

	return (max(nIns, nDel), insText, (nDel, nIns, nRep))


def html2text(html):
	m = re.search(
		"<\s*[tT][iI][tT][lL][eE].*?>(.*?)<\s*/\s*[tT][iI][tT][lL][eE].*?>",
		html,
	)
	if m != None:
		titleRaw = m.group(1)
	else:
		titleRaw = ""

	(w3mIn, w3mOut) = os.popen2("w3m -dump -e -T text/html -cols 80")

	def dumpThread():
		w3mIn.write(titleRaw + "<br>\n" + html)
		w3mIn.close()
	th = threading.Thread(target=dumpThread)
	th.start()
	text = w3mOut.read().splitlines()
	th.join()

	return (text[0], text[1:])


def parallel(funcs, n):
	threads = []
	sem = threading.Semaphore(n)
	for f in funcs:
		sem.acquire()
		def threadProc(f):
			try:
				f()
			finally:
				sem.release()
		th = threading.Thread(target = threadProc, args = (f,))
		threads.append(th)
		th.start()
	
	for t in threads:
		t.join()


if __name__ == "__main__":
	main()
