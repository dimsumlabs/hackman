#!/usr/bin/env python3

import asyncio
import gpiozero
import hid
import redis
import serial
import signal
import sys
import time

r = redis.StrictRedis(host="localhost", port=6379, db=0)
s = serial.Serial('/dev/ttyProMicro')
p = gpiozero.DigitalOutputDevice(17)
h = hid.device()
h.open(0x1b4f, 0x9206)

def button():
  keepopen = False
  lastopen = 0
  while True:
    # read low level HID report
    d = h.read(30, 200)
    # SHIFT + CTRL
    if d and d[0] == 2 and d[1] == 3 and d[2] == 0:
      if d[3] == 0x33: # KEY_SEMICOLON
        # open
        r.publish('door_action', 'OPEN')
      elif d[3] == 0x31: # KEY_BACKSLASH
        # toggle keep open (i.e. unlock)
        keepopen = not keepopen
        if keepopen:
          r.publish('door_action', 'OPEN')
        else:
          r.publish('door_action', 'CLOSE')
      elif d[3] == 0x36: # KEY_COMMA
        # bell
        print("bell")
    else:
      if keepopen and (time.time()-lastopen) > 2.0:
        r.publish('door_action', 'OPEN')

async def doorlight():
  lighton = (p.value == 1)
  try:
    while True:
      if p.value == 0 and lighton == True:
        s.write(b'X') # turn off all lights
        lighton = False
      if p.value == 1 and lighton == False:
        s.write(b'G') # set lights to green
        lighton = True
      await asyncio.sleep(0.3)
  except asyncio.CancelledError:
    print('doorlight done')

async def runall():
  t_button = asyncio.create_task(asyncio.to_thread(button))
  t_doorlight = asyncio.create_task(doorlight())
  #def c():
  #  print('cancelling')
  #  t_button.cancel()
  #  t_doorlight.cancel()
  #asyncio.get_running_loop().add_signal_handler(signal.SIGINT, c)
  await t_button
  await t_doorlight

def main():
  asyncio.run(runall())
  
if __name__ == '__main__':
  sys.exit(main())
