#!/bin/bash
# isntall docker if not exists.
if [[ $(which docker) && $(docker --version) ]]; then
    echo "docker is installed"
    # command
  else
    echo "Install docker"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi
# remove downloaded file
rm get-docker.sh
# check docker is running
if (! docker stats --no-stream 2>/dev/null); then
  # On Mac OS this would be the terminal command to launch Docker
  service docker start
  echo -n "Waiting for Docker to launch"
  sleep 1
  # Wait until Docker daemon is running and has completed initialisation
  while (! docker stats --no-stream >/dev/null 2>&1); do
    # Docker takes a few seconds to initialize
    echo -n "."
    sleep 1
  done
fi
echo
echo "Docker started"
# create selenium chrome container 
docker run --restart=always -d -p 4444:4444 -p 7900:7900 -e SE_DRAIN_AFTER_SESSION_COUNT=5 -e SE_NODE_MAX_SESSIONS=5 -e SE_NODE_OVERRIDE_MAX_SESSIONS=True --shm-size="2g" selenium/standalone-chrome:4.5.0-20221004
cd "$(dirname "$0")" && cd ..
pwd
# # source /root/.cache/pypoetry/virtualenvs/liveshowseller-PfxpePKz-py3.8/bin/activate
poetry run python manage_dev.py renew_facebook_cookies 
