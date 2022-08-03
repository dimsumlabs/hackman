import time
from django.conf import settings
from threading import Timer
import RPi.GPIO as GPIO


class Door:
    def __init__(self):
        GPIO.setmode(getattr(GPIO, settings.DOOR_LOCK["CONFIG"]["gpio_mode"]))
        GPIO.setup(settings.DOOR_LOCK["CONFIG"]["output_pin"], GPIO.OUT)

        # Hack to run cancel without conditionals
        self.timer = Timer(0, lambda: None)

    def open(self, open_time=5, buzz=False):
        # FIXME - the open time is extended by any buzz time
        if buzz:
            self.buzz(0.5, 0.003)

        GPIO.output(settings.DOOR_LOCK["CONFIG"]["output_pin"], True)
        self.timer.cancel()
        self.timer = Timer(open_time, self.close)
        self.timer.start()

    def buzz(self, timeout, rate):
        """
        Use the 'industry standard' method to turn the electric strike into
        a noise maker.  Providing clear evidence to allcomers that the door
        lock has activated and distinctly indicating when they have run out
        of time to open the door.

        The "rate" is the delay used between each on/off cycle.  This needs
        to be fast enough that the door hardware is still energised and the
        lock is open
        """
        # FIXME - the close() method should stop any buzz in progress

        output_pin = settings.DOOR_LOCK["CONFIG"]["output_pin"]

        time_end = time.time() + timeout
        while time.time() < time_end:
            GPIO.output(output_pin, True)
            time.sleep(rate)
            GPIO.output(output_pin, False)
            time.sleep(rate)

    def close(self):
        GPIO.output(settings.DOOR_LOCK["CONFIG"]["output_pin"], False)
