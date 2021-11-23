#!/bin/bash

function start() {
    cd /root/lss
    sudo screen -dmS api
    sudo screen -S api -X stuff "/root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5\r"

    cd /root/lss
    screen -dmS auto_fb
    screen -S auto_fb -X stuff "/root/.local/bin/poetry run python manage.py auto_fb\r"

    cd /root/lss
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

if [ "$1" = "start" ]
then
    start
elif [ "$1" = "stop" ]
then
    stop
elif [ "$1" = "reload" ]
then
    stop
    start
fi
sudo screen -ls