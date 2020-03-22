FROM python:3.8.2-slim-buster

ARG UID=1000
ARG GID=1000
ARG APP_ENV=DEV
ARG APP_MIGRATE=off
ARG APP_COMPILE_LOCALE=off
ARG START_APP=off

ENV APP_ENV=${APP_ENV} \
	APP_MIGRATE=${APP_MIGRATE} \
	APP_COMPILE_LOCALE=${APP_COMPILE_LOCALE} \
	START_APP=${START_APP} \
	# https://docs.python.org/3.8/using/cmdline.html
	PYTHONFAULTHANDLER=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONHASHSEED=random \
	# https://github.com/pypa/pip/blob/master/src/pip/_internal/cli/cmdoptions.py
	PIP_NO_CACHE_DIR=on \
	PIP_DISABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=100 \
	# https://github.com/jwilder/dockerize
	DOCKERIZE_VERSION=v0.6.1 \
	# https://github.com/pypa/pipenv
	PKG_PIPENV_VERSION=2018.11.26

# Create user and group for running app
RUN groupadd -r -g $GID app && useradd --no-log-init -r -u $UID -g app app

# System deps
RUN apt-get update \
	&& apt-get install --assume-yes --no-install-recommends --no-install-suggests \
		tini \
	&& rm -rf /var/lib/apt/lists/*

# This is a special case. We need to run this script as an entry point
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
COPY ./docker-cmd.sh /docker-cmd.sh
RUN chmod +x "/docker-entrypoint.sh" \
	&& chmod +x "/docker-cmd.sh"

# Copy only requirements, to cache them in docker layer
WORKDIR /pysetup
COPY ./Pipfile.lock ./Pipfile /pysetup/

# Building system and app dependencies
RUN set -ex \
	&& savedAptMark="$(apt-mark showmanual)" \
	&& apt-get update \
	&& apt-get install --assume-yes --no-install-recommends --no-install-suggests \
		wget \
	&& wget -nv "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
	&& tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
	&& rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
	&& pip install "pipenv==$PKG_PIPENV_VERSION" \
	&& pipenv install --system --deploy $(test "$APP_ENV" != "PROD" && echo "--dev") \
	&& apt-mark auto '.*' > /dev/null \
	&& apt-mark manual $savedAptMark \
	&& find /usr/local -type f -executable -not \( -name '*tkinter*' \) -exec ldd '{}' ';' \
		| awk '/=>/ { print $(NF-1) }' \
		| sort -u \
		| xargs -r dpkg-query --search \
		| cut -d: -f1 \
		| sort -u \
		| xargs -r apt-mark manual \
	&& apt-get purge --assume-yes --auto-remove \
		--option APT::AutoRemove::RecommendsImportant=false \
		--option APT::AutoRemove::SuggestsImportant=false \
	&& rm -rf /var/lib/apt/lists/*

USER app
COPY --chown=app:app . /app
WORKDIR /app

ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]
CMD ["/docker-cmd.sh"]
