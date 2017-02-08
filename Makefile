SYSTEMD_UNIT_DIR = /lib/systemd/system

all: test

test.style:
	@flake8

test.unit:
	env DJANGO_SETTINGS_MODULE=hackman.settings_test pytest --cov-report=term-missing --cov-fail-under=100 --cov=.

test: test.style test.unit

update-production: export DJANGO_SETTINGS_MODULE=hackman.settings_prod
update-production:
	# Conditional stop since units might not be running
	test `systemctl is-active hackman-doord.service` == "active" && systemctl stop hackman-doord.service
	test `systemctl is-active hackman-rfidd.service` == "active" && systemctl stop hackman-rfidd.service
	test `systemctl is-active hackman.service` == "active" && systemctl stop hackman.service

	# PyZMQ needs some extra massaging due to libpgm
	sudo -u hackman /var/www/hackman/.venv/bin/pip install pyzmq --install-option="--zmq=/usr"
	sudo -u hackman /var/www/hackman/.venv/bin/pip install -r /var/www/hackman/requirements.txt

	# Create django static files in same static directory as project
	sudo -u hackman /var/www/hackman/.venv/bin/python manage.py collectstatic

	# Migrate database changes
	sudo -u hackman /var/www/hackman/.venv/bin/python manage.py migrate

	systemctl start hackman-doord.service
	systemctl start hackman-rfidd.service
	systemctl start hackman.service

install-production: export DJANGO_SETTINGS_MODULE=hackman.settings_prod
install-production:
	apt-get install libpgm-dev git nginx-extras

	mkdir -p /var/www/hackman/.venv
	/usr/local/bin/python3.6 -m venv /var/www/hackman/.venv/
	useradd -d /var/www/hackman hackman
	chown -R hackman:hackman /var/www/hackman

	update-production

	install -m 0644 nginx/default /etc/nginx/sites-available/default

	install -m 0644 systemd/hackman-backup.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-backup.timer $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-doord.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-rfidd.service $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman-paymentreminder.timer $(SYSTEMD_UNIT_DIR)
	install -m 0644 systemd/hackman.service $(SYSTEMD_UNIT_DIR)

	systemctl enable hackman-paymentreminder.timer
	systemctl enable hackman-backup.timer
	systemctl enable hackman-doord.service
	systemctl enable hackman-rfidd.service
	systemctl enable hackman.service
	systemctl enable nginx.service
