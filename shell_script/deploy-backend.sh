#!/bin/bash

cd /home/liveshowseller
git checkout $1
# git pull http://lin:a334596412@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git $1
git pull https://alphatw221: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@github.com/alphatw221/algotech-lss-django.git $1

# poetry install
# sudo mkdir /run/daphne/
service supervisor stop
service supervisor start
supervisorctl reread
supervisorctl reload
service apache2 restart