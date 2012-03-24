#Python example for SPI bus, written by Brian Hensley
#This script will take any amount of Hex values and determine
#the length and then transfer the data as a string to the "spi" module

import spi
from time import sleep

#At the beginning of the program open up the SPI port.
#this is port /dev/spidevX.Y
#Being called as as spi.SPI(X,Y)
a = spi.SPI(2,0)
a.msh = 8000

print "PY: initialising SPI mode, reading data, reading length . . . \n"

#This is my data that I want sent through my SPI bus
latch = [0,0,0]
data = [255,128,128,128,255,128,128,128,255,255,255,255]


#transfers data string
a.writebytes(latch)
for i in range(9):
	a.writebytes(data)

a.writebytes(latch)
	
#At the end of your program close the SPI port 	
#a.close()








