#!/bin/bash

screen -S api -X stuff ^C
screen -S api -X quit

screen -S auto_fb -X stuff ^C
screen -S auto_fb -X quit

screen -S auto_cp -X stuff ^C
screen -S auto_cp -X quit

screen -ls