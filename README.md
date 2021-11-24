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

### `server.sh`

Usage:

```shell
# Start server
server.sh start
# Stop server
server.sh stop
# Reload server
server.sh reload
```

### `cron_tab`

```shell
@reboot /root/lss/server.sh start
```

## Test Notes

### MongoDB testing script

```mongo
db.getCollection('api_campaign_comment').updateMany({}, { $set: {status: NumberInt(0), meta:{}}});
db.getCollection('api_campaign_product').updateMany({}, { $set: {qty_sold: NumberInt(0)}});
db.getCollection('api_cart_product').remove({});
```
