#!/bin/bash

cd /home/liveshowseller
git checkout $1
git pull http://lin:a334596412@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git $1
echo 'a'
poetry install
echo 'b'
service supervisor stop
echo 'c'
service supervisor start
supervisorctl reread
supervisorctl reload
service apache2 restart