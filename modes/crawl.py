import blitterbike
import glob
import time
import random
import os
import sys
from stat import S_ISREG, ST_MTIME, ST_MODE
from twisted.python import log

try:
	from PIL import Image
	from PIL import ImageOps
except ImportError:
	import Image
	import ImageOps


class CrawlMode (blitterbike.BlitterBikeMode):

	def __init__(self):
		self.bootGif = "/home/bhall/dev/gifs/crawl.gif"			

	def start(self):
		self.mirrorFlag = False
		self.scratchFlag = False
		self.invertFlag = False
		self.updateFlag = False

		self.gifList = []
		self.gifIndex = 0
		self.gif = None
		self.im = None
		self.frame = None
		self.lastTime = 0
		self.delay = 0
		self.newFlag = False
		self.loadingFlag = False
		self.sfxQueue = []

		log.msg("CRAWL MODE")
		self.gifList = []
		dirpath = "/home/bhall/dev/gifs/crawl/"
		entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
		entries = ((os.stat(path), path) for path in entries)

		# leave only regular files, insert creation date
		entries = ((stat[ST_MTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))

		for cdate, path in sorted(entries, reverse=True):
			log.msg( "%d : %s" % (cdate, path))
			self.gifList.append(dirpath + os.path.basename(path))

		self.loadingFlag = True
		self.loadGif(self.gifList[self.gifIndex])
		self.loadingFlag = False

	def stop(self):
		pass

	def update(self, speed):

		result = None

		if self.updateFlag:
			self.im = None
			self.updateFlag = False
			self.loadGif(self.gifList[self.gifIndex])		

		if not self.im == None:
			if self.newFlag:
				self.newFlag = False
				result = self.frame

			else:
				currentTime = int(round(time.time() * 1000))
				elapsed = currentTime - self.lastTime

				if elapsed >= self.delay and self.delay > 0:
					self.lastTime = currentTime
					self.nextFrame()
					result = self.frame

		if result != None:
			result = result.convert("RGB")

			if self.invertFlag:
				result = ImageOps.invert(result)			

			if self.mirrorFlag:
				result = result.transpose(Image.FLIP_LEFT_RIGHT)

			result = result.getdata()	

		return result

	def onButtonDown(self, button):

		if button == blitterbike.RIGHT_BUTTON:
			self.gifIndex += 1
			if self.gifIndex == len(self.gifList):
				self.gifIndex = 0

			self.updateFlag = True

		if button == blitterbike.LEFT_BUTTON:
			self.gifIndex -= 1
			if self.gifIndex == -1:
				self.gifIndex = len(self.gifList) - 1

			self.updateFlag = True

		if button == blitterbike.UP_BUTTON:
			if len(self.gifList) > 5:
				self.gifIndex += 5
				if self.gifIndex >= len(self.gifList):
					self.gifIndex -= len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.DOWN_BUTTON:
			if len(self.gifList) > 5:
				self.gifIndex -= 5
				if self.gifIndex < 0:
					self.gifIndex += len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.SPECIAL_BUTTON:
			self.mirrorFlag = not self.mirrorFlag

		if button == blitterbike.D_BUTTON:
			self.scratchFlag = True

		if button == blitterbike.E_BUTTON:
			self.start()

		if button == blitterbike.C_BUTTON:
			self.invertFlag = not self.invertFlag				

	def onButtonUp(self, button):
		pass				

	def loadGif(self, imagePath):
		self.newFlag = True
		self.im = Image.open(imagePath)
		self.frame = Image.new("RGBA", (32, 32), (0,0,0))

		next = self.im.convert("RGBA")
		self.frame.paste(next, next.getbbox(), mask=next)
		self.lastTime = int(round(time.time() * 1000))

		try:
			self.delay = self.im.info['duration']
		except KeyError:
			self.delay = 100

	def nextFrame(self):
		if self.im != None:

			if self.scratchFlag:
				self.im.seek(0)
				self.scratchFlag = False
			else:
				try:
					self.im.seek(self.im.tell() + 1)
				except:
					self.im.seek(0)
					self.frame = Image.new("RGBA", (32, 32), (0,0,0))

			try:
				self.im.palette.dirty = 1
				self.im.palette.rawmode = "RGB"

				next = self.im.convert("RGBA")
				self.frame.paste(next, next.getbbox(), mask=next)

				try:
					self.delay = self.im.info['duration']
				except:
					self.delay = 100


				if self.delay < 20:
					self.delay = 100
			except:
				pass
