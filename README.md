[![Build Status](https://travis-ci.org/dimsumlabs/dsl-accounts.svg?branch=master)](https://travis-ci.org/dimsumlabs/dsl-accounts?branch=master)
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
* Systemd timer for payment reminders

## Prerequisites
* Debian testing or newer (requires Python 3.5)

## Installation
1. `git clone` into `/var/www/hackman`
2. Run `make install-production`
   This should set up everything necessary to run application including nginx,
   backups, continuous deployment etc etc
3. Never run anything manually again \o/
