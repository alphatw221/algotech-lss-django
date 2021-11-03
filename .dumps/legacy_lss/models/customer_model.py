from config import db, ma
from marshmallow.fields import *


class Customer(db.Model):
    __tablename__ = "lss_customer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    fb_user_id = db.Column(db.String(50), nullable=False, unique=True)
    fb_user_name = db.Column(db.String(50), nullable=False)
    fb_token = db.Column(db.String(300), nullable=True)
    remark = db.Column(db.Text, nullable=False)

    def __init__(self, email, fb_user_id, fb_user_name, fb_token, remark):

        self.email = email
        self.fb_user_id = fb_user_id
        self.fb_user_name = fb_user_name
        self.fb_token = fb_token
        self.remark = remark


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'email', 'fb_user_id',
                  'fb_user_name', 'fb_token', 'remark')

        id = Integer()
        email = Str()
        fb_user_id = Str()
        fb_user_name = Str()
        fb_token = Str()
        remark = Str()


class CustomerMeta(db.Model):
    __tablename__ = "lss_customer_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=False)

    def __init__(self, customer_id, meta_key, meta_value):

        self.customer_id = customer_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class CustomerMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'customer_id', 'meta_key', 'meta_value')

        id = Integer()
        customer_id = Integer()
        meta_key = Str()
        meta_value = Str()


class CustomerAddress(db.Model):
    __tablename__ = "lss_customer_address"

    address_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    firstname = db.Column(db.String(32), nullable=False)
    lastname = db.Column(db.String(32), nullable=False)
    company = db.Column(db.String(40), nullable=False)
    address_1 = db.Column(db.String(128), nullable=False)
    address_2 = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)
    country_id = db.Column(db.Integer, nullable=False)
    custom_field = db.Column(db.Text, nullable=False)

    def __init__(self, customer_id, firstname, lastname, company,
                 address_1, address_2, city, postcode, country_id, custom_field):
        self.customer_id = customer_id
        self.firstname = firstname
        self.lastname = lastname
        self.company = company
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.postcode = postcode
        self.country_id = country_id
        self.custom_field = custom_field


class CustomerAddressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('address_id', 'customer_id', 'firstname', 'lastname', 'company',
                  'address_1', 'address_2', 'city', 'postcode', 'country_id', 'custom_field')

        address_id = Integer()
        customer_id = Str()
        firstname = Str()
        lastname = Str()
        company = Str()
        address_1 = Str()
        address_2 = Str()
        city = Str()
        postcode = Str()
        country_id = Integer()
        custom_field = Str()
