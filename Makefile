#!make
include config.env

ifndef MODULE
override MODULE = --mayan-apps
endif

ifndef SKIPMIGRATIONS
override SKIPMIGRATIONS = --skip-migrations
endif

ifndef SETTINGS
override SETTINGS = mayan.settings.testing.development
endif

TEST_COMMAND = ./manage.py test $(MODULE) --settings=$(SETTINGS) $(SKIPMIGRATIONS) $(DEBUG) $(ARGUMENTS)

.PHONY: clean clean-pyc clean-build test

help:
	@echo "Usage: make <target>\n"
	@awk 'BEGIN {FS = ":.*##"} /^[0-9a-zA-Z_-]+:.*?## / { printf "  * %-40s -%s\n", $$1, $$2 }' $(MAKEFILE_LIST)|sort

# Cleaning

clean: ## Remove Python and build artifacts.
clean: clean-build clean-pyc

clean-build: ## Remove build artifacts.
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc: ## Remove Python artifacts.
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -R -f {} +

# Testing

_test-command:
	$(TEST_COMMAND)

test: ## MODULE=<python module name> - Run tests for a single app, module or test class.
test: clean-pyc _test-command

test-debug: ## MODULE=<python module name> - Run tests for a single app, module or test class, in debug mode.
test-debug: DEBUG=--debug-mode
test-debug: clean-pyc _test-command

test-all: ## Run all tests.
test-all: clean-pyc _test-command

test-all-debug: ## Run all tests in debug mode.
test-all-debug: DEBUG=--debug-mode
test-all-debug: clean-pyc _test-command

test-all-migrations: ## Run all migration tests.
test-all-migrations: ARGUMENTS=--no-exclude --tag=migration
test-all-migrations: SKIPMIGRATIONS=
test-all-migrations: clean-pyc _test-command

test-with-mysql: ## MODULE=<python module name> - Run tests for a single app, module or test class against a MySQL database container.
test-with-mysql:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.mysql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test $(MODULE) --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-mysql || true
	@docker volume rm mayan-test-mysql || true

test-with-mysql-all: ## Run all tests against a MySQL database container.
test-with-mysql-all:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.mysql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-mysql || true
	@docker volume rm mayan-test-mysql || true

test-with-mysql-all-migrations: ## Run all migration tests against a MySQL database container.
test-with-mysql-all-migrations:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.mysql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --no-exclude --tag=migration
	@docker rm --force mayan-test-mysql || true
	@docker volume rm mayan-test-mysql || true

test-with-oracle: ## MODULE=<python module name> - Run tests for a single app, module or test class against an Oracle database container.
test-with-oracle:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.oracle','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test $(MODULE) --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-oracle || true
	@docker volume rm mayan-test-oracle || true

test-with-oracle-all: ## Run all tests against an Oracle database container.
test-with-oracle-all:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.oracle','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-oracle || true
	@docker volume rm mayan-test-oracle || true

test-with-oracle-all-migrations: ## Run all migration tests against an Oracle database container.
test-with-oracle-all-migrations:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.oracle','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --no-exclude --tag=migration
	@docker rm --force mayan-test-oracle || true
	@docker volume rm mayan-test-oracle || true

test-with-postgres: ## MODULE=<python module name> - Run tests for a single app, module or test class against a PostgreSQL database container.
test-with-postgres:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test $(MODULE) --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-postgres || true
	@docker volume rm mayan-test-postgres || true

test-with-postgres-all: ## Run all tests against a PostgreSQL database container.
test-with-postgres-all:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --skip-migrations
	@docker rm --force mayan-test-postgres || true
	@docker volume rm mayan-test-postgres || true

test-with-postgres-all-migrations: ## Run all migration tests against a PostgreSQL database container.
test-with-postgres-all-migrations:
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py test --mayan-apps --settings=mayan.settings.testing --no-exclude --tag=migration
	@docker rm --force mayan-test-postgres || true
	@docker volume rm mayan-test-postgres || true

gitlab-ci-run: ## Execute a GitLab CI job locally
gitlab-ci-run:
	if [ -z $(GITLAB_CI_JOB) ]; then echo "Specify the job to execute using GITLAB_CI_JOB."; exit 1; fi; \
	docker rm --force gitlab-runner || true
	docker run --detach --name gitlab-runner --restart no -v $$PWD:$$PWD -v /var/run/docker.sock:/var/run/docker.sock gitlab/gitlab-runner:latest
	docker exec -it -w $$PWD gitlab-runner gitlab-runner exec docker --docker-privileged --docker-volumes /var/run/docker.sock:/var/run/docker.sock --docker-volumes $$PWD/gitlab-ci-volume:/builds $(GITLAB_CI_JOB)
	docker rm --force gitlab-runner || true

# Coverage

coverage-run: ## Run all tests and measure code execution.
coverage-run: clean-pyc
	coverage run $(TEST_COMMAND)

coverage-html: ## Create the coverage HTML report. Run execute coverage-run first.
coverage-html:
	coverage html

# Documentation

docs-serve: ## Run the livehtml documentation generator.
	cd docs;make livehtml

docs-spellcheck: ## Spellcheck the documentation.
	sphinx-build -b spelling -d docs/_build/ docs docs/_build/spelling

# Translations

translations-source-clear: ## Clear the msgstr of the source file
	@sed -i -E  's/msgstr ".+"/msgstr ""/g' `grep -E 'msgstr ".+"' mayan/apps/*/locale/en/*/django.po | cut -d: -f 1` > /dev/null 2>&1  || true

translations-source-fuzzy-remove: ## Remove fuzzy makers
	sed -i  '/#, fuzzy/d' mayan/apps/*/locale/*/LC_MESSAGES/django.po

translations-transifex-check: ## Check that all app have a Transifex entry
	contrib/scripts/translations_helper.py transifex_missing_apps

translations-transifex-generate: ## Check that all app have a Transifex entry
	contrib/scripts/translations_helper.py transifex_generate_config > ./.tx/config

translations-make: ## Refresh all translation files.
	contrib/scripts/translations_helper.py make

translations-compile: ## Compile all translation files.
	contrib/scripts/translations_helper.py compile

translations-transifex-push: ## Upload all translation files to Transifex.
	tx push -s

translations-transifex-pull: ## Download all translation files from Transifex.
	tx pull -f

translations-all: ## Execute all translations targets.
translations-all: translations-source-clear translations-source-fuzzy-remove translations-transifex-generate translations-make translations-transifex-push translations-transifex-pull translations-compile

# Releases

increase-version: ## Increase the version number of the entire project's files.
	@VERSION=`grep "__version__ =" mayan/__init__.py| cut -d\' -f 2|./contrib/scripts/increase_version.py - $(PART)`; \
	BUILD=`echo $$VERSION|awk '{split($$VERSION,a,"."); printf("0x%02d%02d%02d\n", a[1],a[2], a[3])}'`; \
	sed -i -e "s/__build__ = 0x[0-9]*/__build__ = $${BUILD}/g" mayan/__init__.py; \
	sed -i -e "s/__version__ = '[0-9\.]*'/__version__ = '$${VERSION}'/g" mayan/__init__.py; \
	echo $$VERSION > docker/rootfs/version
	make generate-setup

python-test-release: ## Package (sdist and wheel) and upload to the PyPI test server.
python-test-release: clean wheel
	twine upload dist/* -r testpypi
	@echo "Test with: pip install -i https://testpypi.python.org/pypi mayan-edms"

python-release: ## Package (sdist and wheel) and upload a release.
python-release: clean python-wheel
	twine upload dist/* -r pypi

python-sdist: ## Build the source distribution package.
python-sdist: clean
	python setup.py sdist
	ls -l dist

python-wheel: ## Build the wheel distribution package.
python-wheel: clean python-sdist
	pip wheel --no-index --no-deps --wheel-dir dist dist/*.tar.gz
	ls -l dist

python-release-test-via-docker-ubuntu: ## Package (sdist and wheel) and upload to the PyPI test server using an Ubuntu Docker builder.
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source $(DOCKER_LINUX_IMAGE_VERSION) /bin/bash -c "\
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apt-get update && \
	apt-get install make python-pip -y && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make test-release"

python-release-via-docker-ubuntu: ## Package (sdist and wheel) and upload to PyPI using an Ubuntu Docker builder.
	docker run --rm --name mayan_release -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source $(DOCKER_LINUX_IMAGE_VERSION) /bin/bash -c "\
	apt-get update && \
	apt-get -y install locales && \
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	cp -r /host_source/* . && \
	apt-get install make python-pip -y && \
	pip install -r requirements/build.txt && \
	cp -r /host_home/.pypirc ~/.pypirc && \
	make release"

test-sdist-via-docker-ubuntu: ## Make an sdist package and test it using an Ubuntu Docker container.
	docker run --rm --name mayan_sdist_test -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source $(DOCKER_LINUX_IMAGE_VERSION) /bin/bash -c "\
	cp -r /host_source/* . && \
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	apt-get update && \
	apt-get install make python-pip libreoffice tesseract-ocr tesseract-ocr-deu poppler-utils -y && \
	pip install -r requirements/development.txt && \
        pip install -r requirements/testing.txt && \
	make sdist-test-suit \
	"

test-wheel-via-docker-ubuntu: ## Make a wheel package and test it using an Ubuntu Docker container.
	docker run --rm --name mayan_wheel_test -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source $(DOCKER_LINUX_IMAGE_VERSION) /bin/bash -c "\
	cp -r /host_source/* . && \
	echo "LC_ALL=\"en_US.UTF-8\"" >> /etc/default/locale && \
	locale-gen en_US.UTF-8 && \
	update-locale LANG=en_US.UTF-8 && \
	export LC_ALL=en_US.UTF-8 && \
	apt-get update && \
	apt-get install make python-pip libreoffice tesseract-ocr tesseract-ocr-deu poppler-utils -y && \
	pip install -r requirements/development.txt && \
        pip install -r requirements/testing.txt && \
	make wheel-test-suit \
	"

python-sdist-test-suit: ## Run the test suit from a built sdist package
python-sdist-test-suit: python-sdist
	rm -f -R _virtualenv
	virtualenv _virtualenv
	sh -c '\
	. _virtualenv/bin/activate; \
	pip install `ls dist/*.gz`; \
	_virtualenv/bin/mayan-edms.py initialsetup; \
        pip install -r requirements/testing.txt; \
	_virtualenv/bin/mayan-edms.py test --mayan-apps \
	'

python-wheel-test-suit: ## Run the test suit from a built wheel package
python-wheel-test-suit: wheel
	rm -f -R _virtualenv
	virtualenv _virtualenv
	sh -c '\
	. _virtualenv/bin/activate; \
	pip install `ls dist/*.whl`; \
	_virtualenv/bin/mayan-edms.py initialsetup; \
	pip install mock==2.0.0; \
	_virtualenv/bin/mayan-edms.py test --mayan-apps \
	'

generate-setup: ## Create and update the setup.py file.
generate-setup: generate-requirements
	@./contrib/scripts/generate_setup.py
	@echo "Complete."

generate-requirements: ## Generate all requirements files from the project depedency declarations.
	@./manage.py generaterequirements build > requirements/build.txt
	@./manage.py generaterequirements development > requirements/development.txt
	@./manage.py generaterequirements documentation > requirements/documentation.txt
	@./manage.py generaterequirements testing > requirements/testing-base.txt
	@./manage.py generaterequirements production --exclude=django > requirements/base.txt
	@./manage.py generaterequirements production --only=django > requirements/common.txt

# Major releases

gitlab-release-documentation: ## Trigger the documentation build and publication using GitLab CI
gitlab-release-documentation:
	git push
	git push --tags
	git push origin :releases/documentation || true
	git push origin HEAD:releases/documentation

gitlab-release-docker-major: ## Trigger the Docker image build and publication using GitLab CI
gitlab-release-docker-major:
	git push
	git push --tags
	git push origin :releases/docker_major || true
	git push origin HEAD:releases/docker_major

gitlab-release-python-major: ## Trigger the Python package build and publication using GitLab CI
gitlab-release-python-major:
	git push
	git push --tags
	git push origin :releases/python_major || true
	git push origin HEAD:releases/python

gitlab-release-all-major: ## Trigger the Python package, Docker image, and documentation build and publication using GitLab CI
gitlab-release-all-major:
	git push
	git push --tags
	git push origin :releases/all_major || true
	git push origin HEAD:releases/all_major

# Minor releases

gitlab-release-docker-minor: ## Trigger the Docker image build and publication of a minor version using GitLab CI
gitlab-release-docker-minor:
	git push
	git push --tags
	git push origin :releases/docker_minor || true
	git push origin HEAD:releases/docker_minor

gitlab-release-python-minor: ## Trigger the Python package build and publication of a minor version using GitLab CI
gitlab-release-python-minor:
	git push
	git push --tags
	git push origin :releases/python_minor || true
	git push origin HEAD:releases/python_minor

gitlab-release-all-minor: ## Trigger the Python package, Docker image build and publication of a minor version using GitLab CI
gitlab-release-all-minor:
	git push
	git push --tags
	git push origin :releases/all_minor || true
	git push origin HEAD:releases/all_minor

# Dev server

manage: ## Run a command with the development settings.
	./manage.py $(filter-out $@,$(MAKECMDGOALS)) --settings=mayan.settings.development

manage-docker-mysql: ## Run the development server using a Docker PostgreSQL container.
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.mysql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py $(filter-out $@,$(MAKECMDGOALS)) --settings=mayan.settings.development

manage-docker-postgres: ## Run the development server using a Docker PostgreSQL container.
	export MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'$(DEFAULT_DATABASE_NAME)','PASSWORD':'$(DEFAULT_DATABASE_PASSWORD)','USER':'$(DEFAULT_DATABASE_USER)','HOST':'127.0.0.1'}}"; \
	./manage.py $(filter-out $@,$(MAKECMDGOALS)) --settings=mayan.settings.development.docker.db_postgres

runserver: ## Run the development server.
	./manage.py runserver --settings=mayan.settings.development $(ADDRPORT)

runserver_plus: ## Run the Django extension's development server.
	./manage.py runserver_plus --settings=mayan.settings.development $(ADDRPORT)

shell_plus: ## Run the shell_plus command.
	./manage.py shell_plus --settings=mayan.settings.development

staging-start: ## Launch and initialize production-like services using Docker (Postgres and Redis).
staging-start: staging-stop
	docker run --detach --name redis -p 6379:6379 $(DOCKER_REDIS_IMAGE_VERSION)
	docker run --detach --name postgres -p 5432:5432 -e POSTGRES_DB=mayan-staging -e POSTGRES_PASSWORD=mayan-staging -e POSTGRES_USER=mayan-staging $(DOCKER_POSTGRES_IMAGE_VERSION)
	while ! nc -z 127.0.0.1 6379; do sleep 1; done
	while ! nc -z 127.0.0.1 5432; do sleep 1; done
	sleep 4
	pip install psycopg2==$(PYTHON_PSYCOPG2_VERSION) redis==$(PYTHON_REDIS_VERSION)
	./manage.py initialsetup --settings=mayan.settings.staging.docker

staging-stop: ## Stop and delete the Docker production-like services.
	docker stop postgres redis || true
	docker rm postgres redis || true

staging-frontend: ## Launch a front end instance that uses the production-like services.
	./manage.py runserver --settings=mayan.settings.staging.docker

staging-worker: ## Launch a worker instance that uses the production-like services.
	DJANGO_SETTINGS_MODULE=mayan.settings.staging.docker ./manage.py celery worker -A mayan -B -l INFO -O fair

docker-mysql-on: ## Launch and initialize a MySQL Docker container.
	@docker rm --force mayan-test-mysql || true
	@docker volume rm mayan-test-mysql || true
	@docker run --detach --name mayan-test-mysql -p 3306:3306 -e MYSQL_RANDOM_ROOT_PASSWORD=true -e MYSQL_USER=$(DEFAULT_DATABASE_USER) -e MYSQL_PASSWORD=$(DEFAULT_DATABASE_PASSWORD) -e MYSQL_DATABASE=$(DEFAULT_DATABASE_NAME) -v mayan-test-mysql:/var/lib/mysql $(DOCKER_MYSQL_IMAGE_VERSION) --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
	@while ! mysql -h 127.0.0.1 --user=$(DEFAULT_DATABASE_USER) --password=$(DEFAULT_DATABASE_PASSWORD) --execute "SHOW TABLES;" $(DEFAULT_DATABASE_NAME)> /dev/null 2>&1; do echo -n .;sleep 2; done

docker-mysql-off: ## Stop and delete the MySQL Docker container.
	docker rm --force mayan-test-mysql
	@docker volume rm mayan-test-mysql || true

docker-mysql-backup:
	mysqldump --host=127.0.0.1 --no-tablespaces --user=$(DEFAULT_DATABASE_USER) --password=$(DEFAULT_DATABASE_PASSWORD) $(DEFAULT_DATABASE_NAME) > mayan-docker-mysql-backup.sql

docker-mysql-restore:
	@mysql --host=127.0.0.1 --user=$(DEFAULT_DATABASE_USER) --password=$(DEFAULT_DATABASE_PASSWORD) $(DEFAULT_DATABASE_NAME) < mayan-docker-mysql-backup.sql

docker-oracle-on: ## Launch and initialize an Oracle Docker container.
docker-oracle-on:
	@docker rm --force mayan-test-oracle || true
	@docker volume rm mayan-test-oracle || true
	docker run --detach --name mayan-test-oracle -p 49160:22 -p 49161:1521 -e ORACLE_ALLOW_REMOTE=true -v mayan-test-oracle:/u01/app/oracle $(DOCKER_ORACLE_IMAGE_VERSION)
	# https://gist.github.com/kimus/10012910
	pip install cx_Oracle==$(PYTHON_ORACLE_VERSION)
	sleep 10
	while ! nc -z 127.0.0.1 49161; do echo -n .; sleep 2; done

docker-oracle-off:
	@docker rm --force mayan-test-oracle || true
	@docker volume rm mayan-test-oracle || true

docker-postgres-on: ## Launch and initialize a PostgreSQL Docker container.
	@docker rm --force mayan-test-postgresql || true
	@docker volume rm mayan-test-postgresql || true
	@docker run --detach --name mayan-test-postgresql -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_USER=$(DEFAULT_DATABASE_USER) -e=POSTGRES_PASSWORD=$(DEFAULT_DATABASE_PASSWORD) -e POSTGRES_DB=$(DEFAULT_DATABASE_NAME) -p 5432:5432 -v mayan-test-postgresql:/var/lib/postgresql/data $(DOCKER_POSTGRES_IMAGE_VERSION)
	@while ! nc -z 127.0.0.1 5432; do echo -n .; sleep 2; done

docker-postgres-off: ## Stop and delete the PostgreSQL Docker container.
	@docker rm --force mayan-test-postgresql
	@docker volume rm mayan-test-postgresql || true

# Security

safety-check: ## Run a package safety check.
	safety check

# Other

find-gitignores: ## Find stray .gitignore files.
	@export FIND_GITIGNORES=`find -name '.gitignore'| wc -l`; \
	if [ $${FIND_GITIGNORES} -gt 1 ] ;then echo "More than one .gitignore found: $$FIND_GITIGNORES"; fi

python-build:
	docker rm --force mayan-edms-build || true && \
	docker run --rm --name mayan-edms-build -v $(HOME):/host_home:ro -v `pwd`:/host_source -w /source $(DOCKER_PYTHON_IMAGE_VERSION) sh -c "\
	rm /host_source/dist -R || true && \
	mkdir /host_source/dist || true && \
	export LC_ALL=C.UTF-8 && \
	cp -r /host_source/* . && \
	apt-get update && \
	apt-get install -y make && \
	pip install -r requirements/build.txt && \
	make wheel && \
	cp dist/* /host_source/dist/"

check-readme: ## Checks validity of the README.rst file for PyPI publication.
	python setup.py check -r -s

check-missing-migrations: ## Make sure all models have proper migrations.
	./manage.py makemigrations --dry-run --noinput --check

check-missing-inits: ## Find missing __init__.py files from modules.
check-missing-inits:
	@contrib/scripts/find_missing_inits.py

setup-dev-environment: ## Bootstrap a virtualenv by install all dependencies to start developing.
	sudo apt-get install -y exiftool firefox-geckodriver gcc gettext gnupg1 graphviz poppler-utils python3-dev tesseract-ocr-deu
	pip install -r requirements.txt -r requirements/development.txt -r requirements/testing-base.txt -r requirements/documentation.txt -r requirements/build.txt

-include docker/Makefile
