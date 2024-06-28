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
s = serial.Serial("/dev/ttyProMicro")
p = gpiozero.DigitalOutputDevice(17)  # the locking output pin
h = hid.device()
h.open(0x1B4F, 0x9206)
unlock_max_time = 3600  # max unlock is 1 hour


def button():
    keepopen = False
    lastopen = 0
    while True:
        # read low level HID report
        d = h.read(30, 200)
        if d and d[0] == 2 and d[1] == 3 and d[2] == 0:
            # SHIFT + CTRL
            if d[3] == 0x33:  # KEY_SEMICOLON
                # open
                r.publish("door_action", "OPEN")
                print("door open pressed", flush=True)
            elif d[3] == 0x31:  # KEY_BACKSLASH
                # toggle keep open (i.e. unlock)
                keepopen = not keepopen
                if keepopen:
                    print(
                        "unlock pressed, will open for %d seconds" % unlock_max_time,
                        flush=True,
                    )
                    r.publish("door_action", "OPEN")
                else:
                    print("unlock pressed while unlocked, locking", flush=True)
                    r.publish("door_action", "CLOSE")
            elif d[3] == 0x36:  # KEY_COMMA
                # bell, TODO
                print("bell", flush=True)
        else:
            if keepopen:
                sincelastopen = time.time() - lastopen
                if sincelastopen > unlock_max_time:
                    print("unlock exceed max time, locking", flush=True)
                    keepopen = False
                    r.publish("door_action", "CLOSE")
                elif sincelastopen > 2.0:
                    r.publish("door_action", "OPEN")


async def doorlight():
    lighton = p.value == 1
    try:
        while True:
            if p.value == 0 and lighton == True:
                s.write(b"X")  # turn off all lights
                lighton = False
                print("door closed", flush=True)
            if p.value == 1 and lighton == False:
                s.write(b"G")  # set lights to green
                lighton = True
            await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        print("doorlight done", flush=True)


async def runall():
    t_button = asyncio.create_task(asyncio.to_thread(button))
    t_doorlight = asyncio.create_task(doorlight())
    await t_button
    await t_doorlight


def main():
    print("dsl_buttons running", flush=True)
    asyncio.run(runall())


if __name__ == "__main__":
    sys.exit(main())
