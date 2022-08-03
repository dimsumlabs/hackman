#!/usr/bin/env python3
import redis
import json
import os
import time

# Just output to the same channel that the existing dsl-log is watching
channel = 'door_event'
hosts = ['helios.dsl', 'helios2.dsl']
interval = 30


def ping(host):
    error = os.system("ping -w 5 -c 2 -q " + host + ">/dev/null")
    return not error


def check_hosts(hosts):
    """Check all the hosts and return the number currently responding"""

    count = 0
    for host in hosts:
        count += ping(host)

    return count


def main():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    lights = 0

    while True:
        lights_now = check_hosts(hosts)

        if lights != lights_now:
            data = dict()
            data['event'] = 'LIGHTS'
            data['hostcount'] = lights_now
            lights = lights_now

            message = json.dumps(data, sort_keys=True)

            # if debug:
            #  print("message: "+message)
            # else:
            r.publish(channel, message)

        time.sleep(interval - (time.time() % interval))


if __name__ == '__main__':
    main()
