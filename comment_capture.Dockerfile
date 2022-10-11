# syntax=docker/dockerfile:1
FROM alphatw221/lss_comment_capture:latest
ENV LSS_NODE_NAME=TW1
WORKDIR /home/liveshowseller
RUN git pull https://viewer:agtViewer@algotech-git.ap.ngrok.io/nicklien/liveshowseller.git main
RUN service supervisor stop
RUN service supervisor start


