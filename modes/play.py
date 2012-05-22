import blitterbike
import glob
import time
import random
from twisted.python import log

try:
	from PIL import Image
	from PIL import ImageOps
except ImportError:
	import Image
	import ImageOps


class PlayMode (blitterbike.BlitterBikeMode):

	def __init__(self):
		self.bootGif = "/home/bhall/dev/gifs/play.gif"

		self.sfxShree = {}
		self.sfxShree["im"] = Image.open("/home/bhall/dev/gifs/sfx/shree.gif")
		self.sfxShree["isFirst"] = False
		self.sfxShree["index"] = self.sfxShree["im"].tell()

		self.sfxWub = {}
		self.sfxWub["im"] = Image.open("/home/bhall/dev/gifs/sfx/wub.gif")
		self.sfxWub["isFirst"] = False
		self.sfxWub["index"] = self.sfxWub["im"].tell()

		self.sfxUnce = {}
		self.sfxUnce["im"] = Image.open("/home/bhall/dev/gifs/sfx/unce.gif")
		self.sfxUnce["isFirst"] = False
		self.sfxUnce["index"] = self.sfxUnce["im"].tell()

		self.sfxDrop = {}
		self.sfxDrop["im"] = Image.open("/home/bhall/dev/gifs/sfx/drop.gif")
		self.sfxDrop["isFirst"] = False
		self.sfxDrop["index"] = self.sfxDrop["im"].tell()				

	def start(self):
		self.mirrorFlag = False
		self.flipFlag = False
		self.scratchFlag = False
		self.invertFlag = False
		self.strobeFlag = False
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

		log.msg("PLAY MODE")
		self.gifList = glob.glob("/home/bhall/dev/gifs/play/*.gif")
		random.shuffle(self.gifList, random.random)

		log.msg(self.gifList)

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

			if self.flipFlag:
				result = result.transpose(Image.FLIP_TOP_BOTTOM)

			removeQueue = []
			for sfx in self.sfxQueue:

				if sfx["isFirst"]:
					sfx["isFirst"] = False
				else:
					try:
						sfx["im"].seek(sfx["im"].tell() + 1)
					except:
						removeQueue.append(sfx)

				sfx["im"].palette.dirty = 1
				sfx["im"].palette.rawmode = "RGB"

				next = sfx["im"].convert("RGBA")

				result.paste(next, next.getbbox(), mask=next)

			for sfx in removeQueue:
				self.sfxQueue.remove(sfx)

			if self.mirrorFlag:
				result = result.transpose(Image.FLIP_LEFT_RIGHT)

			result = result.getdata()

		if self.strobeFlag:
			result = [self.strobeColor] * 1024			

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
			self.gifIndex += 5
			if self.gifIndex >= len(self.gifList):
				self.gifIndex -= len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.DOWN_BUTTON:
			self.gifIndex -= 5
			if self.gifIndex < 0:
				self.gifIndex += len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.SPECIAL_BUTTON:
			self.mirrorFlag = not self.mirrorFlag

		if button == blitterbike.G_BUTTON:
			self.strobeFlag = True
			self.strobeColor = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))

		if button == blitterbike.H_BUTTON:
			self.flipFlag = not self.flipFlag

		if button == blitterbike.D_BUTTON:
			self.scratchFlag = True

		if button == blitterbike.C_BUTTON:
			self.invertFlag = not self.invertFlag

		if button == blitterbike.A_BUTTON:
			self.sfxUnce["im"].seek(0)
			self.sfxUnce["isFirst"] = True
			self.sfxUnce["frame"] = self.sfxUnce["im"].convert("RGBA")
			self.sfxQueue.append(self.sfxUnce)

		if button == blitterbike.B_BUTTON:
			self.sfxWub["im"].seek(0)
			self.sfxWub["isFirst"] = True
			self.sfxWub["frame"] = self.sfxWub["im"].convert("RGBA")			
			self.sfxQueue.append(self.sfxWub)	

		if button == blitterbike.E_BUTTON:
			self.sfxShree["im"].seek(0)
			self.sfxShree["isFirst"] = True
			self.sfxShree["frame"] = self.sfxShree["im"].convert("RGBA")			
			self.sfxQueue.append(self.sfxShree)	

		if button == blitterbike.F_BUTTON:
			self.sfxDrop["im"].seek(0)
			self.sfxDrop["isFirst"] = True
			self.sfxDrop["frame"] = self.sfxDrop["im"].convert("RGBA")	
			self.sfxQueue.append(self.sfxDrop)						

	def onButtonUp(self, button):

		if button == blitterbike.A_BUTTON:
			try:
				self.sfxQueue.remove(self.sfxUnce)
			except:
				pass

		if button == blitterbike.B_BUTTON:
			try:
				self.sfxQueue.remove(self.sfxWub)
			except:
				pass

		if button == blitterbike.E_BUTTON:
			try:
				self.sfxQueue.remove(self.sfxShree)	
			except:
				pass

		if button == blitterbike.F_BUTTON:
			try:
				self.sfxQueue.remove(self.sfxDrop)
			except:
				pass

		if button == blitterbike.G_BUTTON:
			self.strobeFlag = False							

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
				self.im.palette.dirty = 1
				self.im.palette.rawmode = "RGB"
				self.frame = Image.new("RGBA", (32, 32), (0,0,0))
				next = self.im.convert("RGBA")	
				self.frame.paste(next, next.getbbox(), mask=next)				
				self.scratchFlag = False
			else:
				try:
					self.im.seek(self.im.tell() + 1)
				except:
					self.frame = Image.new("RGBA", (32, 32), (0,0,0))
					self.im.seek(0)

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

