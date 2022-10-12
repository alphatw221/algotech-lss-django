#!/bin/sh
docker run --restart=always -d -p 4444:4444 -p 7900:7900 -e SE_DRAIN_AFTER_SESSION_COUNT=5 -e SE_NODE_MAX_SESSIONS=5 -e SE_NODE_OVERRIDE_MAX_SESSIONS=True --shm-size="2g" selenium/standalone-chrome:4.5.0-20221004
cd /home/liveshowseller
# source /root/.cache/pypoetry/virtualenvs/liveshowseller-PfxpePKz-py3.8/bin/activate
poetry run python manage_dev.py renew_facebook_cookies 
