all: test

# Packages to install if we are running on Debian
build-depends:
	sudo apt-get install -y python3-pytest python3-pytest-cov \
            python3-django python3-django-redis python3-ipy \
            python3-django-ratelimit

# Try to automatically detect if we are running on Debian, or in a virtualenv
# (Debian has /usr/bin/pytest-3 for the python3 version of pytest)
PYTEST := /usr/bin/pytest-3
ifeq (,$(wildcard $(PYTEST)))
    PYTEST := pytest
endif

test.style:
	@flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test $(PYTEST) --cov-report=term-missing --cov-fail-under=100 --cov=.

test: test.style test.unit
