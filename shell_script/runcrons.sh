#!/bin/sh
cd "$(dirname "$0")" && cd ..
pwd
# source /root/.cache/pypoetry/virtualenvs/liveshowseller-PfxpePKz-py3.8/bin/activate
poetry run python manage.py runcrons
