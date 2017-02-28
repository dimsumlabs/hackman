from .settings import *  # noqa
import os


DEBUG = False


def _gen_key():
    """Generate deterministic key per bootup,
    this makes sure not to invalidate sessions and similar things
    between restarts of app while not having to check in anything to git"""
    from datetime import timedelta, datetime
    import string
    import random
    import os

    with open('/proc/uptime') as f:
        uptime = float(f.readline().split()[0])

    chars = ''.join((string.ascii_letters, string.digits, string.punctuation))

    dt = datetime.utcnow()-timedelta(seconds=uptime)
    uname = os.uname()
    seed = ''.join((
        dt.strftime('%s'),
        uname.nodename,
        uname.version))

    key = []
    for _ in range(50):
        random.seed(seed)
        seed = seed[-1] + seed[:-1]
        key.append(random.choice(chars))

    return ''.join(key)


SECRET_KEY = _gen_key()

STATIC_ROOT = '/var/www/hackman/hackman/static/'

# RFID reader config
RFID_READER = {
    'BACKEND': 'hackman_rfid.reader_impls.dimsumlabs_door',
    'HASH_SALT': 'd51e10354f570d35a54d2bc2c01f5fcb8725fb0bf6a58c7db02c5379f81a8a76',  # noqa
    'CONFIG': {  # Implementation specific config
        'serial_port': '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',  # noqa
        'baud_rate': 9600,
        'timeout': 0.5,
    }
}


# Door lock config
DOOR_LOCK = {
    'BACKEND': 'hackman_door.door.impls.dimsumlabs_door',
    'CONFIG': {  # Implementation specific config
        'gpio_mode': 'BCM',
        'output_pin': 17,
    },
    'OPEN_INTERVAL': 5,
    'BIND_URI': 'tcp://127.0.0.1:9001'
}

EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
