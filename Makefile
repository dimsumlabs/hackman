SYSTEMD_UNIT_DIR = /lib/systemd/system

all: test

test.style:
	@flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test pytest --cov-report=term-missing --cov-fail-under=100 --cov=.

test: test.style test.unit

install-production:
	apt-get install libzmq libzmq-dev libpgm libpgm-dev python3 python3-virtualenv python3-pip git
	mkdir -p /var/www/virtualenvs/hackman
	mkdir -p /var/www/hackman
	virtualenv --python=$(which python3) /var/www/virtualenvs/hackman
	chown -R /var/www/hackman
	/var/www/virtualenvs/hackman/bin/pip install -r requirements.txt
	install -m 0644 systemd/hackman-backup.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-backup.timer $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-doord.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-rfidd.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman.service $(SYSTEMD_UNIT_DIR)
	systemctl enable hackman-backup.timer
	systemctl enable hackman-doord.service
	systemctl enable hackman-rfidd.service
	systemctl enable hackman.service
	systemctl restart hackman-backup.timer
	systemctl restart hackman-doord.service
	systemctl restart hackman-rfidd.service
	systemctl restart hackman.service
