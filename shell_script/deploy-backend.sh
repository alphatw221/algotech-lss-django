#!/bin/bash

cd /home/liveshowseller
git checkout $1
git pull http://lin:a334596412@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git $1

poetry install

service supervisor stop
service supervisor start
supervisorctl reread
supervisorctl restart
service apache2 restart