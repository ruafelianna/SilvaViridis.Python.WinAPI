#!/usr/bin/env bash

./scripts/clean.sh \
    && python -m pdm python install 3.13 \
    && python -m pdm venv create 3.13 \
    && python -m pdm use --venv in-project \
    && rm -f .python-version
