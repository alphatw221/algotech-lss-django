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

`cron_tab`

```shell
@reboot /root/lss/_lss_start.sh
```

## Test Notes

### MongoDB testing script

```mongo
db.getCollection('api_campaign_comment').updateMany({}, { $set: {status: NumberInt(0), meta:{}}});
db.getCollection('api_campaign_product').updateMany({}, { $set: {qty_sold: NumberInt(0)}});
db.getCollection('api_cart_product').remove({});
```
