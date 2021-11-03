from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class Order(db.Model):
    __tablename__ = "lss_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    fb_user_id = db.Column(db.String(50), nullable=False)
    fb_user_name = db.Column(db.String(255), nullable=False)
    order_status = db.Column(db.String(120), nullable=False)
    remark = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(1024), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_time = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self, campaign_id, customer_id, fb_user_id, fb_user_name, order_status, remark, total, image=''):

        self.campaign_id = campaign_id
        self.customer_id = customer_id
        self.fb_user_id = fb_user_id
        self.fb_user_name = fb_user_name
        self.order_status = order_status
        self.remark = remark
        self.total = total
        self.image = image


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'campaign_id', 'customer_id', 'fb_user_id', 'fb_user_name', 'order_status', 'remark', 'total', 'image',
                  'created_time', 'modified_time')

        id = Integer()
        campaign_id = Integer()
        customer_id = Integer()
        fb_user_id = Str()
        fb_user_name = Str()
        order_status = Str()
        remark = Str()
        total = Float()
        image = Str()
        created_time = DateTime()
        modified_time = DateTime()


class OrderMeta(db.Model):
    __tablename__ = "lss_order_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        "lss_order.id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self, order_id, meta_key, meta_value):

        self.order_id = order_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class OrderMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'order_id', 'meta_key', 'meta_value')

        id = Integer()
        order_id = Integer()
        meta_key = Str()
        meta_value = Str()


class OrderUserMeta(db.Model):
    __tablename__ = "lss_order_user_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        "lss_order.id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self, order_id, meta_key, meta_value):

        self.order_id = order_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class OrderUserMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'order_id', 'meta_key', 'meta_value')

        id = Integer()
        order_id = Integer()
        meta_key = Str()
        meta_value = Str()


class OrderProduct(db.Model):
    __tablename__ = "lss_order_product"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        "lss_order.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(255), nullable=False)
    order_code = db.Column(db.String(50), nullable=False, default="")
    modelname = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0000)
    total = db.Column(db.Float, nullable=False, default=0.0000)
    tax = db.Column(db.Float, nullable=False, default=0.0000)
    reward = db.Column(db.Integer, nullable=False)
    fb_campaign_order_id = db.Column(db.Integer, nullable=True)
    remark = db.Column(db.Text, nullable=True)

    def __init__(self, order_id, product_id, name, order_code, modelname,
                 quantity, price, total, tax, reward, fb_campaign_order_id, remark):
        self.order_id = order_id
        self.product_id = product_id
        self.name = name
        self.order_code = order_code
        self.modelname = modelname
        self.quantity = quantity
        self.price = price
        self.total = total
        self.tax = tax
        self.reward = reward
        self.fb_campaign_order_id = fb_campaign_order_id
        self.remark = remark


class OrderProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'order_id', 'product_id', 'name', 'order_code', 'modelname',
                  'quantity', 'price', 'total', 'tax', 'reward', 'fb_campaign_order_id', 'remark')

        id = Integer()
        order_id = Integer()
        product_id = Integer()
        name = Str()
        order_code = Str()
        modelname = Str()
        quantity = Integer()
        price = Float()
        total = Float()
        tax = Float()
        reward = Integer()
        fb_campaign_order_id = Integer()
        remark = Str()


"""
class OrderStatus(db.Model):
    __tablename__ = "lss_order_status"

    order_status_id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)

    def __init__(self, order_status_id, language_id, name):
        self.order_status_id = order_status_id
        self.language_id = language_id
        self.name = name


class OrderStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('order_status_id', 'language_id', 'name')

        order_status_id = Integer()
        language_id = Integer()
        name = Str()
"""

""" 
Data for lss_order_status:
INSERT INTO `lss_order_status` (`order_status_id`, `language_id`, `name`) VALUES
(2, 1, 'Processing'),
(3, 1, 'Shipped'),
(7, 1, 'Canceled'),
(5, 1, 'Complete'),
(8, 1, 'Denied'),
(9, 1, 'Canceled Reversal'),
(10, 1, 'Failed'),
(11, 1, 'Refunded'),
(12, 1, 'Reversed'),
(13, 1, 'Chargeback'),
(1, 1, 'Pending'),
(16, 1, 'Voided'),
(15, 1, 'Processed'),
(14, 1, 'Expired');
"""
