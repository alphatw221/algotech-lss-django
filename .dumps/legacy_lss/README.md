# LSS

## Memo

```bash
python _db_create_all.py
```

Alter table

```mysql
ALTER TABLE lss_order
    ADD fb_user_name varchar(255) after fb_user_id;
```

## SERVER COMMANDS

uwsgi --ini app.ini --enable-threads

## URL LINKS

https://sslipa.algotech.app/
https://sslipa.algotech.app/report/campaign_summary_{fb_campaign_id}.csv

## (FILE) lss_start:

```console
#!/bin/bash

cd /home/ubuntu/lss
screen -dmS auto
screen -S auto -X stuff "/usr/bin/python3 \_automation.py\r"

cd /home/ubuntu/lss
screen -dmS api
screen -S api -X stuff "/usr/local/bin/uwsgi --ini app.ini --enable-threads\r"

cd /home/ubuntu/lss-mb
screen -dmS mb
screen -S mb -X stuff "/home/ubuntu/.nvm/versions/node/v14.15.3/bin/node app.js\r"

screen -ls
```

## (FILE) lss_end:

```console
#!/bin/bash

screen -S api -X stuff ^C
screen -S api -X quit

screen -S auto -X stuff ^C
screen -S auto -X quit

screen -S mb -X stuff ^C
screen -S mb -X quit
```

## (FILE) crontab

```console
@reboot /home/ubuntu/lss_start
```
