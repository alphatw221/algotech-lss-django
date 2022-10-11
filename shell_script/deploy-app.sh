#!/bin/bash

cd /home/lss_vue_enigma
git checkout $1
git pull http://lin:a334596412@algotech-git.ap.ngrok.io/Lin/lss_vue_enigma.git $1

npm install
npm run build

cd /home/liveshowseller
git checkout $1
git pull http://lin:a334596412@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git $1

poetry install

poetry run python manage.py collectstatic
yes
service supervisor stop
service supervisor start
supervisorctl reread
supervisorctl reload
service apache2 restart