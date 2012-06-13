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


class BikeMode (blitterbike.BlitterBikeMode):

	def __init__(self):
		self.fullSpeed = 90.0;
		self.bootGif = blitterbike.BLITTER_BIKE_PATH  + "/gifs/bike.gif"
		self.gifPath = blitterbike.BLITTER_BIKE_PATH + "/gifs/bike/"
		self.im = None
		self.gifList = []
		self.gifList.append({"gif":"boo.gif", "step":12, "wait":100, "loops":[{"speed":0.05, "start":0, "end":0}, {"speed":1.0, "start":1, "end":26}]})
		self.gifList.append({"gif":"corgi.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":3}]})
		self.gifList.append({"gif":"mario.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":2}]})
		self.gifList.append({"gif":"megaman.gif", "step":12, "wait":300, "loops":[{"speed":0.02, "start":0, "end":6}, {"speed":0.65, "start":7, "end":10}, {"speed":1.0, "start":11, "end":29}]})
		self.gifList.append({"gif":"nyan.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":11}]})
		self.gifList.append({"gif":"pony_gallop.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":5}]})
		self.gifList.append({"gif":"pony_run.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":3}]})
		self.gifList.append({"gif":"rabbit.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":7}]})
		self.gifList.append({"gif":"samus.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":9}]})
		self.gifList.append({"gif":"sonic.gif", "step":6, "wait":200, "loops":[{"speed":0.02, "start":0, "end":7}, {"speed":0.5, "start":8, "end":15}, {"speed":0.75, "start":16, "end":19}, {"speed":1.0, "start":20, "end":23}]})
		self.gifList.append({"gif":"yoshi.gif", "step":12, "wait":100, "loops":[{"speed":1.0, "start":0, "end":9}]})


	def start(self):
		self.mirrorFlag = False
		self.flipFlag = False
		self.scratchFlag = False
		self.invertFlag = False
		self.updateFlag = False

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
		self.current = None

		log.msg("BIKE MODE")
		random.shuffle(self.gifList, random.random)

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
			if self.newFlag and self.frame != None:
				self.newFlag = False
				result = self.frame

			else:

				currentTime = int(round(time.time() * 1000))
				elapsed = currentTime - self.lastTime				

				if len(self.current["loops"]) > 1:
					if speed < self.current["loops"][0]["speed"]:
						if elapsed > self.current["wait"]:
							self.lastTime = currentTime
							self.nextFrame(speed)
							result = self.frame
					else:
						if elapsed >= (self.current["step"]/speed) * 1000:
							self.lastTime = currentTime
							self.nextFrame(speed)
							result = self.frame						

				else:	
					if speed > 0:
						currentTime = int(round(time.time() * 1000))
						elapsed = currentTime - self.lastTime

						if elapsed >= (self.current["step"]/speed) * 1000:
							self.lastTime = currentTime
							self.nextFrame(speed)
							result = self.frame

		if result != None:
			result = result.convert("RGB")

			if self.mirrorFlag:
				result = result.transpose(Image.FLIP_LEFT_RIGHT)

			if self.flipFlag:
				result = result.transpose(Image.FLIP_TOP_BOTTOM)

			if self.invertFlag:
				result = ImageOps.invert(result)

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
			self.gifIndex += 5
			if self.gifIndex >= len(self.gifList):
				self.gifIndex -= len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.DOWN_BUTTON:
			self.gifIndex -= 5
			if self.gifIndex < 0:
				self.gifIndex += len(self.gifList)

			self.updateFlag = True

		if button == blitterbike.A_BUTTON:
			self.mirrorFlag = not self.mirrorFlag

		if button == blitterbike.E_BUTTON:
			self.flipFlag = not self.flipFlag

		if button == blitterbike.D_BUTTON:
			self.scratchFlag = True

		if button == blitterbike.H_BUTTON:
			self.invertFlag = not self.invertFlag		


	def onButtonUp(self, button):
		pass

	def loadGif(self, info):

		self.current = info
		self.frame = None
		imagePath = "%s%s" % (self.gifPath, self.current["gif"])

		log.msg(imagePath)
		self.im = Image.open(imagePath)
		self.frame = Image.new("RGBA", (32, 32), (0,0,0))

		self.lastFrame = next = self.im.convert("RGBA")
		self.frame.paste(next, next.getbbox(), mask=next)
		self.lastTime = int(round(time.time() * 1000))
		self.newFlag = True

	def nextFrame(self, speed):
		if self.im != None:

			try:
				self.im.seek(self.im.tell() + 1)
			except EOFError:
				self.im.seek(0)
				self.frame = Image.new("RGBA", (32, 32), (0,0,0))

			percent = speed/self.fullSpeed

			if percent > 1.0:
				percent = 1.0

			index = 0
			while percent > self.current["loops"][index]["speed"]:
				index += 1

			start = self.current["loops"][index]["start"]
			end = self.current["loops"][index]["end"]

			while self.im.tell() > end:
				try:
					self.im.seek(self.im.tell() + 1)
				except EOFError:
					self.im.seek(0)
					self.frame = Image.new("RGBA", (32, 32), (0,0,0))

			while self.im.tell() < start:
				self.im.palette.dirty = 1
				self.im.palette.rawmode = "RGB"

				next = self.im.convert("RGBA")
				
				self.frame.paste(next, next.getbbox(), mask=next)				
				self.im.seek(self.im.tell() + 1)

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

