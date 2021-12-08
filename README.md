# LSS API server

## URLs

- API Root: <https://gipassl.algotech.app/>
- Chat Bot - Facebook: <https://gipassl.algotech.app/chat_bot/facebook/>
- Web Front-end: <>
- Shopping Cart: <>

## Run server

```shell
# development
python manage.py runserver 0.0.0.0:8000
# production
gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5
# production w/ root user
sudo /root/.local/bin/poetry run gunicorn lss.wsgi --bind 0.0.0.0:8000 --workers 5
```

## Manage locale

```shell
# generate/update .po file
python manage.py makemessages -l LANG_CODE
# generate/update .mo file
python manage.py compilemessages
```

## Scripts

### `server.sh`

Usage:

```shell
# Start server
./server.sh start
# Stop server
./server.sh stop
# Reload server
./server.sh reload
```

### `cron_tab`

```shell
@reboot /root/lss/server.sh start
```

## Test Notes

### MongoDB testing script

```mongodb
db.getCollection('api_campaign_comment').updateMany({}, { $set: {status: NumberInt(0), meta:{}}});
db.getCollection('api_campaign_product').updateMany({}, { $set: {qty_sold: NumberInt(0)}});
db.getCollection('api_campaign_lucky_draw').remove({});
db.getCollection('api_cart_product').remove({});
```
