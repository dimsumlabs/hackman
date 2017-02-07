from django.conf import settings
from threading import Timer
import RPi.GPIO as GPIO


class Door:

    def __init__(self):
        GPIO.setmode(getattr(GPIO, settings.DOOR_LOCK['CONFIG']['gpio_mode']))
        GPIO.setup(settings.DOOR_LOCK['CONFIG']['output_pin'])

        # Hack to run cancel without conditionals
        self.timer = Timer(0, lambda: None)

    def open(self, open_time=5):
        GPIO.output(settings.DOOR_LOCK['CONFIG']['output_pin'], True)
        self.timer.cancel()
        self.timer = Timer(open_time, self.close)
        self.timer.start()

    def close(self):
        GPIO.output(settings.DOOR_LOCK['CONFIG']['output_pin'], False)
