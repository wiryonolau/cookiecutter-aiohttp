#!/usr/bin/env bash
git init
virtualenv -p python3.9 "$(pwd)/${@:-.env}"
make yarn-install
/bin/bash -c "source $(pwd)/.env/bin/activate; make install"
