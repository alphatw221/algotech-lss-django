#!/bin/bash

PROJECT_ROOT="/root/lss"

function start() {
    cd "$PROJECT_ROOT"

    screen -dmS api
    screen -S api -X stuff "/root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5\r"

    screen -dmS auto_fb
    screen -S auto_fb -X stuff "/root/.local/bin/poetry run python manage.py auto_fb\r"

    screen -dmS auto_cp
    screen -S auto_cp -X stuff "/root/.local/bin/poetry run python manage.py auto_cp\r"
}

function stop() {
    screen -S api -X stuff ^C
    screen -S api -X quit

    screen -S auto_fb -X stuff ^C
    screen -S auto_fb -X quit

    screen -S auto_cp -X stuff ^C
    screen -S auto_cp -X quit
}

if [ "$1" = "start" ]; then
    start
elif [ "$1" = "stop" ]; then
    stop
elif [ "$1" = "reload" ]; then
    stop && start
else
    echo "Error: command not supported."
fi
screen -ls