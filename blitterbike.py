from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.python import log
from threading import Timer
import inspect, os, sys, pkgutil, socket, time

try:
    from PIL import Image
except ImportError:
    import Image


MODE_BUTTON = "mode"
SPECIAL_BUTTON = "special"
UP_BUTTON = "up"
DOWN_BUTTON = "down"
LEFT_BUTTON = "left"
RIGHT_BUTTON = "right"

A_BUTTON = "a"
B_BUTTON = "b"
C_BUTTON = "c"  
D_BUTTON = "d"
E_BUTTON = "e"
F_BUTTON = "f"
G_BUTTON = "g"
H_BUTTON = "h"

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

# The core BlitterBike application
# It loads in all of the modes and flips between them as the user hits the mode button
class BlitterBike:
    
    def start(self):
        self.modeList = []

        pkg = 'modes'
        __import__(pkg)
        package = sys.modules[pkg]
        prefix = pkg + "."

        for importer,modname,ispkg in pkgutil.iter_modules(package.__path__,prefix):
            module = __import__(modname,locals(),[],-1)
            for name,cls in inspect.getmembers(module):
                if inspect.isclass(cls):
                    self.modeList.append(cls())


        self.modeIndex = 0
        self.mode = self.modeList[self.modeIndex]
        self.delayTimer = None

        reactor.callInThread(self.run)
        self.isRunning = True

        if socket.gethostname() == "blitterbike":
            import spi
            self.spi_conn = spi.SPI(2, 0)
            self.spi_conn.msh = 1000000

            self.blit = self.blitScreen
            reactor.callInThread(self.readSensor)

            self.clear()

        else:
	    from Tkinter import Tk, Canvas, Frame, BOTH	
            self.blit = self.blitTk

        self.onChangeMode()

    def run(self):
        while self.isRunning:
            if self.mode != None:
                im = self.mode.update()
            
                if im != None:
                    self.blit(im)

    def stop(self):
        self.clear()
        self.isRunning = False

        if self.mode != None:
            self.mode.stop()

    def readSensor(self):
        while self.isRunning:
            pass

    def onChangeMode(self):
        self.mode.stop()
        self.modeIndex += 1
        if self.modeIndex == len(self.modeList):
            self.modeIndex = 0

        self.mode = None
        self.loadModeBootGif(self.modeList[self.modeIndex].getBootGif())

    def onButtonDown(self, button):
        log.msg("BUTTON DOWN: " + button)

        if self.mode != None:
            self.mode.onButtonDown(button)

    def onButtonUp(self, button):
        log.msg("BUTTON UP: " + button)
        if self.mode != None:
            self.mode.onButtonUp(button)

    def blitTk(self, im):
        pass

    def blitScreen(self, im):
        y = 31;
        x = 0;
        dir = 1
        data = []

        for i in range(1024):
            pixel = im[(y*32) + x]

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

    def fill(self, color):
        self.blit([color] * 1024)

    def clear(self):
        self.writeToStrip(LATCH)

        self.fill((0, 0, 0))

    def loadModeBootGif(self, bootGif):
        self.bootImage = Image.open(bootGif)
        self.bootFrame = Image.new("RGBA", (32, 32), (0,0,0))

        self.lastBootFrame = next = self.bootImage.convert("RGBA")
        self.bootFrame.paste(next, next.getbbox())
        self.bootStartIndex = self.bootImage.tell()

        if self.delayTimer != None:
            self.delayTimer.cancel()

        try:
            delay = self.bootImage.info['duration']
        except KeyError:
            delay = 30

        self.delayTimer = Timer(delay/1000, self.nextBootFrame)
        self.delayTimer.daemon = True
        self.delayTimer.start()

        self.drawBoot()

    def nextBootFrame(self):
        try:
            self.bootImage.seek(self.bootImage.tell() + 1)
            self.bootImage.palette.dirty = 1
            self.bootImage.palette.rawmode = "RGB"

            next = self.bootImage.convert("RGBA")
            self.bootFrame.paste(next, next.getbbox(), mask=next)
            

            self.lastBootFrame = next

            self.drawBoot()

            try:
                delay = self.bootImage.info['duration']
            except KeyError:
                delay = 100


            if delay < 20:
                delay = 100


            self.delayTimer = Timer(delay/1000, self.nextBootFrame)
            self.delayTimer.daemon = True
            self.delayTimer.start()

        except EOFError:

            # done playing the boot GIF, now start
            self.mode = self.modeList[self.modeIndex]
            self.mode.start()

    def drawBoot(self):
        self.blit(self.bootFrame.convert("RGB").getdata())

class BlitterBikeServer(LineReceiver):

    def __init__(self, blitterbike):
        self.blitterbike = blitterbike

    def lineReceived(self, command):
        commandList = command.split(",")

        if commandList[0] == "d":
            if commandList[1] == MODE_BUTTON:
                self.blitterbike.onChangeMode()
            else:
                self.blitterbike.onButtonDown(commandList[1])
        elif commandList[1] == "u":
            if commandList[1] != MODE_BUTTON:
                self.blitterbike.onButtonUp(commandList[1])


class BlitterBikeServerFactory(Factory):

    def __init__(self):
        self.blitterbike = BlitterBike()

    def buildProtocol(self, addr):
        return BlitterBikeServer(self.blitterbike)

    def startFactory(self):
        self.blitterbike.start()

    def stopFactory(self):
        self.blitterbike.stop()

