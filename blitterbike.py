#!/usr/bin/env python

import sys, time
import socket

from daemon import Daemon

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 31337


class BlitterBike(Daemon):

	def start(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((HOST, PORT))
		self.sock.listen(1)
		self.conn, self.addr = self.sock.accept()

		super(Daemon, self).start()	

	def stop(self):
		# close all connections, unbind
		self.conn.close()
		self.sock.close()

		super(Daemon, self).stop()

	def run(self):
		while True:
			data = conn.recv(1)
			if not data: 
				break
			conn.sendall(data)


if __name__ == "__main__":
	daemon = BlitterBike('/tmp/blitterbike.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
