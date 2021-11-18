# LSS API server

## Run server

```bash
# development
python manage.py runserver 0.0.0.0:8000
# production
gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5
# production w/ root user
sudo /root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5
```

## Scripts

`/home/ubuntu/lss_start.sh`

```shell
#!/bin/bash

cd /home/ubuntu/lss
sudo screen -dmS api
sudo screen -S api -X stuff "sudo /root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5\r"

cd /home/ubuntu/lss
screen -dmS auto_fb
screen -S auto_fb -X stuff "sudo /root/.local/bin/poetry run python manage.py auto_fb\r"

sudo screen -ls
```

`/home/ubuntu/lss_end.sh`

```shell
#!/bin/bash

screen -S api -X stuff ^C
screen -S api -X quit

screen -S auto_fb -X stuff ^C
screen -S auto_fb -X quit

screen -ls
```

`cron_tab`

```shell
@reboot /home/ubuntu/lss_start.sh
```
