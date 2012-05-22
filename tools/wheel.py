import time

# put Port 8 Pin 3 into mode 7 (GPIO)
open('/sys/kernel/debug/omap_mux/lcd_data0', 'wb').write("%X" % 39)

try:
  # check to see if the pin is already exported
  open('/sys/class/gpio/gpio70/direction').read()
except:
  # it isn't, so export it
  print("exporting GPIO 70")
  open('/sys/class/gpio/export', 'w').write('70')

# set Port 8 Pin 3 for output
open('/sys/class/gpio/gpio70/direction', 'w').write('in')
# we will assume that USR1 and USR 2 are already configured as LEDs
lastValue = 1
lastMagnet = 0
halfCirc = 23.56194490

cp = time.time()
np = 0

while 1:
  # turn on USR1 and external LED
  value = int(open('/sys/class/gpio/gpio70/value', 'r').read())
  np = time.time()
  cp = np


  if value == 0 and lastValue == 1:
    magnet = time.time()
    if lastMagnet > 0:
      speed  =  (halfCirc/(magnet - lastMagnet)) #* 0.0568181818
      print "%f" % (speed,)
    lastMagnet = magnet 
  lastValue = value
  time.sleep(0.001)	

# cleanup - remove GPIO38 folder from file system
open('/sys/class/gpio/unexport', 'w').write('70')
