SYSTEMD_UNIT_DIR = /lib/systemd/system

all: test

test.style:
	@flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test pytest --cov-report=term-missing --cov-fail-under=100 --cov=.

test: test.style test.unit

install-production:
	apt-get install libzmq-dev libpgm-dev git nginx-extras

	mkdir -p /var/www/hackman/.venv
	/usr/local/bin/python3.6 -m venv /var/www/hackman/.venv/
	useradd hackman
	chown -R hackman:hackman /var/www/hackman

	sudo -u hackman /var/www/hackman/.venv/bin/pip install -r /var/www/hackman/requirements.txt

	install -m 0644 systemd/hackman-backup.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-backup.timer $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-doord.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-rfidd.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-paymentreminder.timer $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman.service $(SYSTEMD_UNIT_DIR)

	systemctl enable hackman-backup.timer
	systemctl enable hackman-doord.service
	systemctl enable hackman-rfidd.service
	systemctl enable hackman.service
	systemctl enable hackman.service

	systemctl restart hackman-paymentreminder.timer
	systemctl restart hackman-backup.timer
	systemctl restart hackman-doord.service
	systemctl restart hackman-rfidd.service
	systemctl restart hackman.service
