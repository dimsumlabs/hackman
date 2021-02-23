[![Build Status](https://travis-ci.org/dimsumlabs/hackman.svg?branch=master)](https://travis-ci.org/dimsumlabs/hackman?branch=master)
# NaNNaNNaNNaNNaNNaNNaNNaN Hackman!
The Dim Sum Labs payment, door and membership system.
Allows members to register their (cash or paypal) payment and receive login credentials.
These can be used to open the door via either web interface or rfid card.

### The system's workflow

#### payments
1. The dsl-accounts repository is updated by the space orga when payments are made.
1. The hackman-paymentimport service (included here) downloads the dsl-accounts data every hour.

#### missing payments
If there is an issue with the paymentimport or the space orga have missed an update.
You can submit that you have paid.
1. Go to http://door/ and log in with your credentials.
1. Go to Account actions
1. Select the month you are paying for and inform the door of your payment

Note: Informing the door this way is temporary and will only last until the next payment import.

## To-Do
* Continuous deployment based on Travis-ci builds
* UDEV-based autostart for the components that depend on hardware:
  * hackman-rfidd expects to find a usb serial adaptor
  * dsl-lights expects to find a pimoroni Mote Host USB device

## Prerequisites
* Debian buster or newer (requires Python 3.5)

## Installation on raspberry pi
These steps can be quite slow to complete - the ansible system uses quite a
lot of CPU and RAM, which can be in short supply on the Raspberry Pi.

The intent is to have a documented process that depends only on the Raspberry
Pi hardware and thus can be easily tested or trialed.  That being said, there
are several ways to speed up or otherwise improve on this in the future.

1. Start with a fresh raspian lite buster install image, with ssh enabled
1. Dont forget to change the passwords and set up any extra users on the pi
1. `sudo apt-get update && sudo apt-get -y upgrade`
1. `sudo apt-get -y install git ansible`
1. `git clone` this repo into a convinient place ( e.g `~/hackman` )
1. cd into the repo
1. `ansible-playbook ansible-installer.yml`
1. If replacing an old system, restore the old database to `/var/www/hackman/db/db.sqlite3`
1. Add the `~hackman/.ssh/id_ed25519.pub` to the root@door-backup.dsl authorised keys
1. Add the door-backup.dsl ssh host key to the `~hackman/.ssh/known_hosts`
1. reboot to activate all changes
3. Never run anything manually again \o/

## Upgrades
1. Ensure the CI tests are showing green (See the top of this README)
2. ssh to door system
3. cd into the repo
1. `git pull`
1. `ansible-playbook ansible-installer.yml`
6. `systemctl restart hackman`
6. `systemctl restart hackman-doord`
6. `systemctl restart hackman-rfidd`

## Day to Day Operations

- Run a payment import right now: `systemctl start hackman-paymentimport.service`
- Check the last payment import: `ls -al /var/www/hackman/db/payments.json`
- Dump all the users and their paid-until dates: `cd /var/www/hackman; python3 manage.py paymentlist`
