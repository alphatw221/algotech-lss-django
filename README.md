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

`/root/lss_start.sh`

```shell
#!/bin/bash

cd /root/lss
sudo screen -dmS api
sudo screen -S api -X stuff "sudo /root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5\r"

cd /root/lss
screen -dmS auto_fb
screen -S auto_fb -X stuff "sudo /root/.local/bin/poetry run python manage.py auto_fb\r"

cd /root/lss
screen -dmS auto_cp
screen -S auto_cp -X stuff "sudo /root/.local/bin/poetry run python manage.py auto_cp\r"

sudo screen -ls
```

`/root/lss_end.sh`

```shell
#!/bin/bash

screen -S api -X stuff ^C
screen -S api -X quit

screen -S auto_fb -X stuff ^C
screen -S auto_fb -X quit

screen -S auto_cp -X stuff ^C
screen -S auto_cp -X quit

screen -ls
```

`cron_tab`

```shell
@reboot /root/lss_start.sh
```

## Testing Area

### MongoDB testing script

```mongo
db.getCollection('api_campaign_comment').updateMany({}, { $set: {status: NumberInt(0), meta:{}}});
db.getCollection('api_campaign_product').updateMany({}, { $set: {qty_sold: NumberInt(0)}});
db.getCollection('api_cart_product').remove({});
```
