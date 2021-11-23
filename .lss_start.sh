#!/bin/bash

cd /root/lss
sudo screen -dmS api
sudo screen -S api -X stuff "sudo /root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5\r"

cd /root/lss
screen -dmS auto_fb
screen -S auto_fb -X stuff "sudo /root/.local/bin/poetry run python manage.py auto_fb\r"

cd /root/lss
screen -dmS auto_cp
screen -S auto_cp -X stuff "sudo /root/.local/bin/poetry run python manage.py auto_cp\r"

sudo screen -ls