from .settings import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+v*pw9!3la*0*09z+uh6-tl)@m-32j9n%4sx4j#2()#c4ysif5'

ALLOWED_HOSTS = ['door2', '192.168.100.132']

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


NOTIFICATIONS_BIND_URI = 'epgm://eth0;239.192.1.1:5555'


# TODO: Get settings from env vars
