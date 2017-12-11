#!/usr/bin/env python
# TCP server by hand
# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import sys
import StringIO
import socket
import asyncore
import asynchat
import ctypes


def eraseLine( out ):
	out.write( "\r\x1b[K" )


class AsynReadLine( object ):

	cReadLine = ctypes.CDLL( "libreadline.so" )

	def __init__( self, handler, prompt, sockMap = asyncore.socket_map ):
		self.sockMap = sockMap
		self.cHandler = ctypes.CFUNCTYPE( None, ctypes.c_char_p )( handler )
		self.cReadLine.rl_callback_handler_install( prompt, self.cHandler )
		sockMap[sys.stdin.fileno()] = self
	
	
	def __del__( self ):
		try:
			self.close()
		except: pass


	def close( self ):
		del self.sockMap[sys.stdin.fileno()]
		self.cReadLine.rl_callback_handler_remove()


	def redisplay( self ):
		self.cReadLine.rl_forced_update_display()


	def addHistory( self, line ):
		self.cReadLine.add_history( line )

	
	def readable( self ):
		return True


	def writable( self ):
		return False


	def handle_read_event( self ):
		self.cReadLine.rl_callback_read_char()


class AsynPingPong( asynchat.async_chat ):

	def __init__( self, sock ):
		asynchat.async_chat.__init__( self, sock )
		self.iBuf = StringIO.StringIO()
		self.readLine = AsynReadLine( self.onCommand, "> " )
		self.set_terminator( "\n" )


	def collect_incoming_data( self, data ):
		self.iBuf.write( data )


	def found_terminator( self ):
		self.iBuf.write( "\n" )
		eraseLine( sys.stdout )
		sys.stdout.write( self.iBuf.getvalue() )
		sys.stdout.flush()
		self.readLine.redisplay()

		self.iBuf = StringIO.StringIO()

	
	def handle_close( self ):
		eraseLine( sys.stdout )
		sys.stdout.write( "- Connection closed by client.\n" )
		sys.stdout.flush()
		self.close()


	def close( self ):
		self.readLine.close()
		asynchat.async_chat.close( self )


	def onCommand( self, line ):
		if line == None:
			eraseLine( sys.stdout )
			sys.stdout.write( "- Connection closed by server.\n" )
			sys.stdout.flush()
			self.close()
		else:
			self.push( line + "\r\n" )
			self.readLine.addHistory( line )


def syncAccept( bindAddr ):
	slin = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	slin.bind( bindAddr )
	slin.listen( 1 )

	while True:
		sys.stdout.write( "\n- Waiting connection...\n" )
		sys.stdout.flush()
		(sstr, addr) = slin.accept()
		sys.stdout.write( "- Connected from %s:%s.\n" % addr )
		sys.stdout.flush()
		AsynPingPong( sstr )
		asyncore.loop()


def main():
	try:
		if len( sys.argv ) == 2:
			host = ""
			port = int( sys.argv[1] )
		elif len( sys.argv ) == 3:
			host = sys.argv[1]
			port = int( sys.argv[2] )
		else:
			raise StandardError()
	except StandardError:
		print "usage: %s [host] port" % sys.argv[0]
		return

	syncAccept( (host, port) )


if __name__ == "__main__":
	main()
