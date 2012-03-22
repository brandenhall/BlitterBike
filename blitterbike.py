#!/usr/bin/env python

import sys, time
import socket
import atexit

from signal import signal, SIGTERM
from daemon import Daemon

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 31337


class BlitterBike(Daemon):
	
	def cleanup(self):
		self.sock.close()

	def run(self):
		# set things up so we can cleanup on stop
		atexit.register(self.cleanup)
		signal(SIGTERM, lambda signum, stack_frame: sys.exit(1))

		# open the socket server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((HOST, PORT))
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

		# setup the main input loop
		while True:
			data = self.conn.recv(1)
			if not data: 
				break
			self.conn.sendall(data)


if __name__ == "__main__":
	daemon = BlitterBike('/tmp/blitterbike.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'debug' == sys.argv[1]:
			try:
				daemon.run()
			except KeyboardInterrupt:
				sys.exit(0)
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
