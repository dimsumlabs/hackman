all: test

test.style:
	@flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test pytest --cov-report=term-missing --cov-fail-under=100 --cov=.

test: test.style test.unit
