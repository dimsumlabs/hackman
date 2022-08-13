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
1. Go to https://door.dimsumlabs.com/ and log in with your credentials.
1. Go to Account actions
1. Select the month you are paying for and inform the door of your payment

Note: Informing the door this way is temporary and will only last until the next payment import.

## To-Do
* UDEV-based autostart for the components that depend on hardware:
  * hackman-rfidd expects to find a usb serial adaptor
  * dsl-lights expects to find a pimoroni Mote Host USB device

## Hacking

Hackman uses [Poetry](https://python-poetry.org/docs/pyproject/) as it's Python dependency manager.

### Using direnv
To use direnv to manage the development environment simply run `direnv allow`.
This will call out to Nix and Poetry internally.

### Manual hacking
Install Poetry and manage the development manually, it's left as an exercise reader how that is done.

## Prerequisites
* Debian bullseye or newer (requires Python 3.6+)
* The latest `.deb` from the [Github Releases page](https://github.com/dimsumlabs/hackman/releases)

## Installation on raspberry pi
The intent is to have a documented process that depends only on the Raspberry
Pi hardware and thus can be easily tested or trialed.  That being said, there
are several ways to speed up or otherwise improve on this in the future.

1. Start with a fresh raspian lite bullseye install image, with ssh enabled
1. Dont forget to change the passwords and set up any extra users on the pi
1. `sudo apt-get update && sudo apt-get -y upgrade`
1. `sudo apt install -y -f hackman_0.1.0-1_armhf.deb`
1. reboot to activate all changes
3. Never run anything manually again \o/

## Upgrades
1. This auto-updates from the latest Github release automatically.
1. If that were to fail you can manually install the updated deb.

## Day to Day Operations

- Run a payment import right now: `systemctl start hackman-paymentimport.service`
- Check the last payment import: `ls -al /var/lib/hackman/db/payments.json`
- Dump all the users and their paid-until dates: `hackman-manage paymentlist`
