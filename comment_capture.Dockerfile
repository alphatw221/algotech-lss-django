# syntax=docker/dockerfile:1
FROM alphatw221/lss_comment_capture:latest
ENV LSS_NODE_NAME=TW1
WORKDIR /home/liveshowseller
RUN git branch
RUN git pull https://lin:a334596412@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git main
COPY ./config.py /home/liveshowseller/config.py
RUN service supervisor stop
RUN service supervisor start
# RUN supervisorctl reread
# RUN supervisorctl reload
