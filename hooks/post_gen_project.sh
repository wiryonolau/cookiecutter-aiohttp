#!/usr/bin/env bash
git init
virtualenv -p python3.9 .env || true
make yarn-install
source .env/bin/activate
