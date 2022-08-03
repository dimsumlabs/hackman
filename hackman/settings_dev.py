import hashlib

from .settings import *  # noqa


DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "+v*pw9!3la*0*09z+uh6-tl)@m-32j9n%4sx4j#2()#c4ysif5"

# RFID reader config
RFID_READER = {
    "BACKEND": "hackman_rfid.reader_impls.dummy",
    "HASH_SALT": hashlib.sha256(b"a").hexdigest(),
}


# Door lock config
DOOR_LOCK = {
    "BACKEND": "hackman_door.door.impls.dummy_dev",
    "BIND_URI": "tcp://127.0.0.1:9001",
}
