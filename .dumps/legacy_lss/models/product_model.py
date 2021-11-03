from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class Product(db.Model):
    __tablename__ = "lss_product"

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    fb_user_id = db.Column(db.String(50), nullable=False)
    max_order_amount = db.Column(db.Integer, nullable=True, default=0)
    active_stat = db.Column(db.Integer, nullable=True, default=0)
    product_type = db.Column(db.String(50), nullable=True)
    remark = db.Column(db.String(200), nullable=True)

    modelname = db.Column(db.String(64), nullable=True)
    sku = db.Column(db.String(64), nullable=True)
    upc = db.Column(db.String(12), nullable=True)
    location = db.Column(db.String(128), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    stock_status_id = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    manufacturer_id = db.Column(db.Integer, nullable=True)
    shipping = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0000)
    price_two = db.Column(db.Float, nullable=False, default=0.0000)
    price_three = db.Column(db.Float, nullable=False, default=0.0000)
    points = db.Column(db.Integer, nullable=True)
    date_available = db.Column(db.DateTime, nullable=True)
    height = db.Column(db.Float, nullable=True, default=0.00000000)
    subtract = db.Column(db.Integer, nullable=True, default=1)
    minimum = db.Column(db.Integer, nullable=True, default=1)
    sort_order = db.Column(db.Integer, nullable=True, default=0)
    status = db.Column(db.Integer, nullable=True, default=0)
    viewed = db.Column(db.Integer, nullable=True, default=0)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self,
                 fb_user_id,
                 max_order_amount,
                 active_stat,
                 product_type,
                 remark,

                 modelname,
                 sku,
                 upc,
                 location,
                 quantity,
                 stock_status_id,
                 image,
                 manufacturer_id,
                 shipping,
                 price,
                 price_two,
                 price_three,
                 points,
                 date_available,
                 height,
                 subtract,
                 minimum,
                 sort_order,
                 status,
                 viewed):
        self.fb_user_id = fb_user_id
        self.max_order_amount = max_order_amount
        self.active_stat = active_stat
        self.product_type = product_type
        self.remark = remark

        self.modelname = modelname
        self.sku = sku
        self.upc = upc
        self.location = location
        self.quantity = quantity
        self.stock_status_id = stock_status_id
        self.image = image
        self.manufacturer_id = manufacturer_id
        self.shipping = shipping
        self.price = price
        self.price_two = price_two
        self.price_three = price_three
        self.points = points
        self.date_available = date_available
        self.height = height
        self.subtract = subtract
        self.minimum = minimum
        self.sort_order = sort_order
        self.status = status
        self.viewed = viewed


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('product_id',

                  'fb_user_id',
                  'max_order_amount',
                  'active_stat',
                  'product_type',
                  'remark',

                  'modelname',
                  'sku',
                  'upc',
                  'location',
                  'quantity',
                  'stock_status_id',
                  'image',
                  'manufacturer_id',
                  'shipping',
                  'price',
                  'price_two',
                  'price_three',
                  'points',
                  'date_available',
                  'height',
                  'subtract',
                  'minimum',
                  'sort_order',
                  'status',
                  'viewed',
                  'date_added',
                  'date_modified')

        product_id = Integer()

        fb_user_id = Integer()
        max_order_amount = Integer()
        active_stat = Integer()
        product_type = Str()
        remark = Str()

        modelname = Str()
        sku = Str()
        upc = Str()
        location = Str()
        quantity = Integer()
        stock_status_id = Integer()
        image = Str()
        manufacturer_id = Integer()
        shipping = Integer()
        price = Float()
        price_two = Float()
        price_three = Float()
        points = Integer()
        date_available = DateTime()
        height = Float()
        subtract = Integer()
        minimum = Integer()
        sort_order = Integer()
        status = Integer()
        viewed = Integer()
        date_added = DateTime()
        date_modified = DateTime()


class ProductPreviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('product_id', 'modelname', 'quantity', 'stock_status_id', 'image', 'manufacturer_id',
                  'shipping', 'price', 'points', 'date_available', 'status', 'viewed', 'owner_id', 'max_order_amount', 'active_stat')

        product_id = Integer()
        modelname = Str()
        quantity = Integer()
        stock_status_id = Integer()
        image = Str()
        manufacturer_id = Integer()
        shipping = Integer()
        price = Float()
        points = Integer()
        date_available = DateTime()
        status = Integer()
        viewed = Integer()

        owner_id = Integer()
        max_order_amount = Integer()
        active_stat = Integer()


class ProductDescription(db.Model):
    __tablename__ = "lss_product_description"

    product_id = db.Column(db.Integer, db.ForeignKey(
        "lss_product.product_id"), primary_key=True)
    language_id = db.Column(db.Integer, primary_key=True, default=0)
    name = db.Column(db.String(255), nullable=True, default="")
    description = db.Column(db.Text, nullable=True, default="")
    tag = db.Column(db.Text, nullable=True, default="")
    order_code = db.Column(db.String(50), nullable=True, default="")
    meta_title = db.Column(db.String(255), nullable=True, default="")
    meta_description = db.Column(db.String(255), nullable=True, default="")
    meta_keyword = db.Column(db.String(255), nullable=True, default="")

    def __init__(self, product_id, language_id, name, description, tag, order_code, meta_title, meta_description, meta_keyword):
        self.product_id = product_id
        self.language_id = language_id
        self.name = name
        self.description = description
        self.tag = tag
        self.order_code = order_code
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.meta_keyword = meta_keyword


class ProductDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('product_id', 'language_id', 'name', 'description',
                  'tag', 'order_code', 'meta_title', 'meta_description', 'meta_keyword')

        product_id = Integer()
        language_id = Integer()
        name = Str()
        description = Str()
        tag = Str()
        order_code = Str()
        meta_title = Str()
        meta_description = Str()
        meta_keyword = Str()


class ProductManufacturer(db.Model):
    __tablename__ = "lss_product_manufacturer"

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer, nullable=True)

    def __init__(self, name, image, sort_order):
        self.name = name
        self.image = image
        self.sort_order = sort_order


class ProductManufacturerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'name', 'image', 'sort_order')

        id = Integer()
        name = Str()
        image = Str()
        sort_order = Integer()


class ProductMeta(db.Model):
    __tablename__ = "lss_product_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        "lss_product.product_id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self, product_id, meta_key, meta_value):

        self.product_id = product_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class ProductMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'product_id', 'meta_key', 'meta_value')

        id = Integer()
        product_id = Integer()
        meta_key = Str()
        meta_value = Str()
