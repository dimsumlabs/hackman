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

## Installation
1. `git clone` into `/var/www/hackman`
2. collect underpants?  (There used to be an install makefile target, but that
   has been removed)
3. Never run anything manually again \o/
