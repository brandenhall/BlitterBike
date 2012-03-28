#!/usr/bin/env python

import sys, time
import socket
import atexit
import spi
import Image

from signal import signal, SIGTERM
from daemon import Daemon

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 31337
FPS = 30

GAMMA_TABLE =  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 
		0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
		1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,
		2,  2,  2,  2,  2,  3,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,
		4,  4,  4,  4,  5,  5,  5,  5,  5,  6,  6,  6,  6,  6,  7,  7,
		7,  7,  7,  8,  8,  8,  8,  9,  9,  9,  9, 10, 10, 10, 10, 11,
		11, 11, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 15, 15, 16, 16,
		16, 17, 17, 17, 18, 18, 18, 19, 19, 20, 20, 21, 21, 21, 22, 22,
		23, 23, 24, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30,
		30, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 37, 37, 38, 38, 39,
		40, 40, 41, 41, 42, 43, 43, 44, 45, 45, 46, 47, 47, 48, 49, 50,
		50, 51, 52, 52, 53, 54, 55, 55, 56, 57, 58, 58, 59, 60, 61, 62,
		62, 63, 64, 65, 66, 67, 67, 68, 69, 70, 71, 72, 73, 74, 74, 75,
		76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
		92, 93, 94, 95, 96, 97, 98, 99,100,101,102,104,105,106,107,108,
		109,110,111,113,114,115,116,117,118,120,121,122,123,125,126,127]

LATCH = [0] * 48


#class BlitterBike(Daemon):
class BlitterBike():
	
	def draw(self):
		self.blit(self.frame.convert("RGB").getdata())

		try:
			self.im.seek(self.im.tell() + 1)
		except EOFError:
			self.im.seek(self.startIndex)

		next = self.im.convert("RGBA")
		self.frame.paste(next, None, next)

	def fill(self, color):
		self.blit([color] * 1024)

	def blit(self, image):
		y = 31;
		x = 0;
		dir = 1
		data = []

		for i in range(1024):
			pixel = image[(y*32) + x]

			red = GAMMA_TABLE[pixel[0]] | 128
			green = GAMMA_TABLE[pixel[1]] | 128
			blue = GAMMA_TABLE[pixel[2]] | 128
			
			data.append(green)
			data.append(red)
			data.append(blue)

			x += dir
			if dir == 1 and x == 32:
				x = 31
				y -= 1
				dir = -1
			elif dir == -1 and x == -1:
				x = 0
				y -= 1
				dir = 1

		self.writeToStrip(data)
		self.writeToStrip(LATCH)

	def writeToStrip(self, data):
		for index in range(0, len(data), 32):
			self.spi_conn.writebytes(data[index:(index+32)])

	def run(self):
		# set things up so we can cleanup on stop
		atexit.register(self.cleanup)
		signal(SIGTERM, lambda signum, stack_frame: sys.exit(1))

		self.spi_conn = spi.SPI(2, 0)
		self.spi_conn.msh = 1000000

		# wake up the screen
		self.writeToStrip(LATCH)

		self.fill((0, 0, 0))


		self.im = Image.open("gifs/bike.gif")
		self.frame = self.im.copy().convert("RGBA")
		self.startIndex = self.im.tell()

		# open the socket server
#		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#		self.sock.bind((HOST, PORT))
#		self.sock.listen(1)
#		self.conn, self.addr = self.sock.accept()

		last_time = time.time()
		self.index = 0

		# setup the main input loop
		while True:
			self.draw()

#			data = self.conn.recv(1)
#			if data: 
#				self.conn.sendall(data)

			new_time = time.time()
			# see how many milliseconds we have to sleep for
    			# then divide by 1000.0 since time.sleep() uses seconds
    			sleep_time = ((1000.0 / FPS) - (new_time - last_time)) / 1000.0
    			if sleep_time > 0:
        			time.sleep(sleep_time)
    			last_time = new_time

#			break

	def cleanup(self):
#		self.sock.close()
		pass


if __name__ == "__main__":
	if len(sys.argv) == 2:
#		daemon = BlitterBike('/tmp/blitterbike.pid')
		daemon = BlitterBike()

		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'debug' == sys.argv[1]:
			daemon.run()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
