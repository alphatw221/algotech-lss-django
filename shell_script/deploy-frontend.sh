#!/bin/bash

cd /home/lss_vue_enigma
git checkout $1
# git pull http://lin:a334596412@algotech-git.ap.ngrok.io/Lin/lss_vue_enigma.git $1
git pull https://alphatw221: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@github.com/alphatw221/algotech-lss-vue-enigma.git $1

npm install
npm run build

