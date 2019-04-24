all: test

# Packages to install if we are running on Debian
PACKAGES := \
    python3-django \
    python3-flake8 \
    python3-jinja2 \
    python3-pytest-django \
    python3-gunicorn \
    python3-coverage \
    python3-pytest-cov \
    python3-django-redis \
    python3-ipy \
    python3-django-cors-headers \
    python3-django-oauth-toolkit \
    redis-server \
    gunicorn3 \
    python3-gevent \

# TODO
# - from the requirements.txt
#   - pyserial>=3.2.1
#   - RPi.GPIO>=0.6.3
# - not available or too old in debian:
#   - python3-django-ratelimit package


build-depends:
	sudo apt-get install -y $(PACKAGES)

# Create or update the database
dev.db:
	python3 manage.py migrate

# Run the site with a development server
dev.run:
	python3 manage.py runserver

# Try to automatically detect if we are running on Debian, or in a virtualenv
# (Debian has /usr/bin/pytest-3 for the python3 version of pytest)
PYTEST := /usr/bin/pytest-3
ifeq (,$(wildcard $(PYTEST)))
    PYTEST := pytest
endif

test.style:
	flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test $(PYTEST) --cov-report=term-missing --cov-fail-under=98 --cov=.

test: test.style test.unit
