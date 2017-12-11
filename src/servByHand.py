#!/usr/bin/env python
# TCP server by hand
# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import sys
import socket
import asyncore
import ctypes


def eraseLine( out ):
	out.write( "\r\x1b[K" )


class AsynReadLine( object ):

	_cReadLine = ctypes.CDLL( "libreadline.so" )

	def __init__( self, handler, map = asyncore.socket_map ):
		self._map = map
		self._cHandler = ctypes.CFUNCTYPE( None, ctypes.c_char_p )( handler )
		self._cReadLine.rl_callback_handler_install( "> ", self._cHandler )
		map[sys.stdin.fileno()] = self
	
	
	def __del__( self ):
		try:
			self.close()
		except: pass


	def close( self ):
		del self._map[sys.stdin.fileno()]
		self._cReadLine.rl_callback_handler_remove()


	def redisplay( self ):
		self._cReadLine.rl_forced_update_display()

	
	def readable( self ):
		return True


	def writable( self ):
		return False


	def handle_read_event( self ):
		self._cReadLine.rl_callback_read_char()


class AsynPingPong( asyncore.dispatcher_with_send ):

	def __init__( self, sock ):
		asyncore.dispatcher_with_send.__init__( self, sock )
		self.readLine = AsynReadLine( self.onCommand )


	def handle_read( self ):
		# we can't detect whether connection is closed until calling recv() and
		# must not do anything when connection is closed.
		buf = self.recv( 4096 )
		if len( buf ) != 0:
			eraseLine( sys.stdout )
			sys.stdout.write( buf )
			while len( buf ) == 4096:
				buf = self.recv( 4096 )
				sys.stdout.write( buf )
			sys.stdout.write( "\n" )
			sys.stdout.flush()

			self.readLine.redisplay()

	
	def handle_close( self ):
		eraseLine( sys.stdout )
		sys.stdout.write( "- Connection closed by client.\n" )
		sys.stdout.flush()
		self.close()


	def close( self ):
		self.readLine.close()
		asyncore.dispatcher_with_send.close( self )


	def onCommand( self, line ):
		if line == None:
			eraseLine( sys.stdout )
			sys.stdout.write( "- Connection closed by server.\n" )
			sys.stdout.flush()
			self.close()
		else:
			self.send( line + "\r\n" )


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
