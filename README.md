[![Build Status](https://travis-ci.org/dimsumlabs/hackman.svg?branch=master)](https://travis-ci.org/dimsumlabs/hackman?branch=master)
# NaNNaNNaNNaNNaNNaNNaNNaN Hackman!
The Dim Sum Labs payment, door and membership system.
Allows members to register their (cash or paypal) payment and receive login credentials.
These can be used to open the door via either web interface or rfid card.

### The system's workflow

#### Cash payments
1. Pay money in envelope, write name on it
2. (Optionally) Submit that you have paid through going to http://door/ and log in with your credentials
   Choose which month to submit payment for and which amount you are supposed to pay and submit.

   If this is not done it will be synced from accounting repo at a later date

#### Paypal
Not yet implemented

## To-Do
* Continuous deployment based on Travis-ci builds
* Integrate dsl-accounts repository
* Integrate paypal payments

## Prerequisites
* Debian testing or newer (requires Python 3.5)

## Installation on raspberry pi
1. Start with a fresh raspian lite buster install image, with ssh enabled
1. Dont forget to change the passwords and set up any extra users on the pi
1. `sudo apt-get update && sudo apt-get -y upgrade`
1. `sudo apt-get -y install git ansible`
1. `git clone` this repo into a convinient place ( e.g `~/hackman` )
1. cd into the repo
1. `ansible-playbook ansible-installer.yml`
1. restore old database if needed
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

