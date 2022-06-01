FROM python:3.9-slim

ARG PUID=1000
ARG PGID=1000

ENV HTTPHOST=0.0.0.0 \
    HTTPPORT=8080 \
    BASIC_AUTH_FILE= \
    CERTIFICATE_FILE= \
    PRIVATEKEY_FILE= \
    DEBUG=

RUN useradd -m -s /bin/bash app \
    && usermod -u ${PUID} app \
    && groupmod -g ${PGID} app \
    && usermod -a -G tty app \
    && mkdir /app \
    && chown -R app:app /app \
    && pip install --upgrade pip

COPY ./docker-entrypoint.sh /docker-entrypoint.sh

# Cache apt-get
RUN apt-get update \
    && apt-get install --no-install-recommends -y yarnpkg \
    && apt-get -y --purge autoremove \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/list/* /var/tmp/*

WORKDIR /home/app
USER app

# Cache yarnpkg and node modules
COPY --chown=app:app ./hfmonitor/http/package.json /tmp/package.json
RUN yarnpkg install --production=true --cwd=/tmp --cache-folder=/tmp/.cache

COPY --chown=app:app ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-warn-script-location --cache-dir=/tmp/.cache --user -r /tmp/requirements.txt

COPY --chown=app:app ./ /tmp/app
RUN cd /tmp/app \
    && rm -rf /tmp/app/hfmonitor/http/node_modules \
    && mv /tmp/node_modules /tmp/app/hfmonitor/http/node_modules \
    && pip3 install --no-warn-script-location --cache-dir=/tmp/.cache --user . \
    && rm -rf /tmp/* || true

ENTRYPOINT ["/docker-entrypoint.sh"]
