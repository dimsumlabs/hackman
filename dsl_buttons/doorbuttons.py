import signal
import sys
import hid

def sig(s, frame):
  sys.exit(0)

signal.signal(signal.SIGINT, sig)

try:
  h = hid.device()
  h.open(0x1b4f, 0x9206)
  while True:
    d = h.read(30, 500)
    if d and d[0] == 2 and d[1] == 3 and d[2] == 0:
      if d[3] == 0x33:
          # open
          print("open")
      elif d[3] == 0x31:
          # unlock
          print("unlock")
      elif d[3] == 0x36:
          # bell
          print("bell")
    
except IOError as ex:
    print(ex)
