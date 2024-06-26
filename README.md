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
  * dsl-buttons expects to find a Pro Micro device with programs in `mcus/promicro` (and other MCU devices in `mcus/`)

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
1. `sudo apt install -y ./hackman_0.1.0-1_armhf.deb`
1. reboot to activate all changes
3. Never run anything manually again \o/

## Upgrades
1. This auto-updates from the latest Github release automatically.
1. If that were to fail you can manually install the updated deb.

## Day to Day Operations

- Run a payment import right now: `systemctl start hackman-paymentimport.service`
- Check the last payment import: `ls -al /var/lib/hackman/db/payments.json`
- Dump all the users and their paid-until dates: `hackman-manage paymentlist`

## Deployment
After CI builds a new image, perform these steps to prepare a new SD card:
1. burn the image to SD card (e.g. balenaEtcher)
1. pg_dump the old database `pg_dump -Ft postgresql://hackman:hackman@localhost/hackman > /tmp/hackman_dump_<date>.tar`
1. transfer tar ball to new card
1. prepare database and user:
    - `sudo -u postgres psql`
    - `create database hackman;`
    - `create user hackman with encrypted password ``hackman`` `
    - `grant all privileges on database hackman to hackman;`
1. load tar ball to postgresql `pg_restore -v -d postgresql://hackman:hackman@localhost/hackman /tmp/hackman_dump_<date>.tar`
1. copy `~/.ssh/authorized_keys`
1. edit SMTP credentials `sudo EDITOR=vim systemctl edit hackman`
    ```
    [Service]
    Environment="EMAIL_HOST=<value>"
    Environment="EMAIL_PORT=<value>"
    Environment="EMAIL_HOST_USER=<value>"
    Environment="EMAIL_HOST_PASSWORD=<value>"
    Environment="DEFAULT_FROM_EMAIL=<value>"
    ```
