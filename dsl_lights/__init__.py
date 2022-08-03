#!/usr/bin/env python3
from mote import Mote
import redis
import json
import time


mote = Mote()

mote.configure_channel(1, 16, False)
mote.configure_channel(2, 16, False)
mote.configure_channel(3, 16, False)
mote.configure_channel(4, 16, False)


rgb_vals = {
    "DOOR_OPEN": (0, 255, 0),  # Green
    "DOOR_OPEN_GRACE": (255, 255, 0),  # Yellow
    "DOOR_OPEN_DENIED": (255, 0, 0),  # Red
    "CARD_UNPAIRED": (59, 0, 100),  # supposedly "orange"
}

USER_RGB = {2: (255, 0, 120), 63: (255, 0, 120)}  # Adam  # Aurelio


def blink_lights(rgb):
    for i in range(16):
        for channel in range(4):
            mote.set_pixel(channel + 1, i, *rgb)
        mote.show()
        time.sleep(0.05)
    time.sleep(0.5)
    mote.clear()
    mote.show()


def main():
    r = redis.StrictRedis(host="localhost", port=6379, db=0)
    ps = r.pubsub()

    try:
        ps.subscribe("door_event")
        for m in ps.listen():
            if not m or m["type"] != "message":
                continue

            m = json.loads(m["data"])

            if "event" not in m:
                continue

            # default colors
            rgb = (0, 0, 0)

            # event specific colors
            if m["event"] in rgb_vals:
                rgb = rgb_vals[m["event"]]

            # User specific colors
            if m["event"] == "DOOR_OPEN" and m["user_id"] in USER_RGB:
                rgb = USER_RGB[m["user_id"]]

            blink_lights(rgb)

    finally:
        ps.unsubscribe()


if __name__ == "__main__":
    main()
