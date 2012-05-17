import blitterbike
import glob
import time
import random
from twisted.python import log

try:
	from PIL import Image
	from PIL import ImageEnhance
	from PIL import ImageOps
except ImportError:
	import Image
	import ImageEnhance
	import ImageOps


class PlayMode:
	def getBootGif(self):
		return "gifs/play.gif"

	def start(self):
		self.mirrorFlag = False
		self.bwFlag = False
		self.flipFlag = False
		self.scratchFlag = False
		self.invertFlag = False

		self.gifList = []
		self.gifIndex = 0
		self.gif = None
		self.im = None
		self.frame = None
		self.lastFrame = None
		self.startIndex = 0
		self.lastTime = 0
		self.delay = 0
		self.newFlag = False
		self.loadingFlag = False

		log.msg("STARTING PLAY!")
		self.gifList = glob.glob("gifs/play/*.gif")
		random.shuffle(self.gifList, random.random)

		log.msg(self.gifList)

		self.loadingFlag = True
		self.loadGif(self.gifList[self.gifIndex])
		self.loadingFlag = False

	def stop(self):
		pass

	def update(self):

		result = None

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

			if self.mirrorFlag:
				result = result.transpose(Image.FLIP_LEFT_RIGHT)

			if self.flipFlag:
				result = result.transpose(Image.FLIP_TOP_BOTTOM)

			if self.bwFlag:
				enhancer = ImageEnhance.Color(result)
				result = enhancer.enhance(0)

			if self.invertFlag:
				result = ImageOps.invert(result)

			result = result.getdata()

		return result

	def onButtonDown(self, button):
		updateFlag = False

		if button == blitterbike.RIGHT_BUTTON:
			self.gifIndex += 1
			if self.gifIndex == len(self.gifList):
				self.gifIndex = 0

			updateFlag = True

		if button == blitterbike.LEFT_BUTTON:
			self.gifIndex -= 1
			if self.gifIndex == -1:
				self.gifIndex = len(self.gifList) - 1

			updateFlag = True

		if button == blitterbike.UP_BUTTON:
			self.gifIndex += 5
			self.gifIndex %= len(self.gifList)

			updateFlag = True

		if button == blitterBike.DOWN_BUTTON:
			self.gifIndex -= 5
			if self.gifIndex < 0:
				self.gifIndex += len(self.gifList)

			updateFlag = True

		if button == blitterbike.SPECIAL_BUTTON:
			self.mirrorFlag = not self.mirrorFlag

		if button == blitterbike.G_BUTTON:
			self.bwFlag = not self.bwFlag

		if button == blitterbike.H_BUTTON:
			self.flipFlag = not self.flipFlag

		if button == blitterbike.D_BUTTON:
			self.scratchFlag = True

		if button == blitterbike.C_BUTTON:
			self.invertFlag = not self.invertFlag		


		if updateFlag:
			self.im = None
			self.loadGif(self.gifList[self.gifIndex])

	def onButtonUp(self, button):
		pass

	def loadGif(self, imagePath):
		self.newFlag = True
		self.im = Image.open(imagePath)
		self.frame = Image.new("RGBA", (32, 32), (0,0,0))

		self.lastFrame = next = self.im.convert("RGBA")
		self.frame.paste(next, next.getbbox(), mask=next)
		self.startIndex = self.im.tell()
		self.lastTime = int(round(time.time() * 1000))

		try:
			self.delay = self.im.info['duration']
		except KeyError:
			self.delay = 30

	def nextFrame(self):
		if self.im != None:

			if self.scratchFlag:
				self.im.seek(self.startIndex)
				self.scratchFlag = False
			else:
				try:
					self.im.seek(self.im.tell() + 1)
				except EOFError:
					self.im.seek(self.startIndex)

			self.im.palette.dirty = 1
			self.im.palette.rawmode = "RGB"

			next = self.im.convert("RGBA")
			
			self.frame.paste(next, next.getbbox(), mask=next)


			self.lastFrame = next

			try:
				self.delay = self.im.info['duration']
			except KeyError:
				self.delay = 100


			if self.delay < 20:
				self.delay = 100

