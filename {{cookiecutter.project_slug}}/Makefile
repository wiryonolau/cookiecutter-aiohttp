.PHONY: help

help: ## This help.
    @awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
SHELL := /bin/bash
THIS_FILE := $(lastword $(MAKEFILE_LIST))
PROJECT_NAME := "$$(basename `pwd` | cut -d. -f1 )"

# Include environment file if exist
-include env.locals

%:
	@echo ""
all:
	@echo ""
wheel:
	/usr/bin/env pip3 install setuptools wheel
	/usr/bin/env python3 setup.py sdist bdist_wheel
install:
	$(MAKE) -s yarn-build
	/usr/bin/env pip3 install pip-tools
	pip-compile -v
	/usr/bin/env pip3 install --cache-dir $$(pwd)/.cache -r requirements.txt
start:
	/usr/bin/env python3 -m ${PROJECT_NAME}
start-dev:
	/usr/bin/env pip3 install aiohttp-debugtoolbar aiohttp-devtools
	/usr/bin/env adev runserver -p8080 --livereload --root $$(pwd) ${PROJECT_NAME}
yarn-install:
	docker run --rm -it \
		-v $$(pwd)/${PROJECT_NAME}/http:/srv/${PROJECT_NAME} \
		-w /srv/${PROJECT_NAME} \
		-e NODE_ENV=development \
		--user $$(id -u):$$(id -g) \
	node:lts-slim yarn install --production=false
yarn-build:
	docker run --rm -it \
		-v $$(pwd)/${PROJECT_NAME}/http:/srv/${PROJECT_NAME} \
		-w /srv/${PROJECT_NAME} \
		-e NODE_ENV=development \
		--user $$(id -u):$$(id -g) \
	node:lts-slim yarn run build
yarn:
	docker run --rm -it \
		-v $$(pwd)/${PROJECT_NAME}/http:/srv/${PROJECT_NAME} \
		-w /srv/${PROJECT_NAME} \
		-e NODE_ENV=development \
		--user $$(id -u):$$(id -g) \
	node:lts-slim yarn $(filter-out $@,$(MAKECMDGOALS))
