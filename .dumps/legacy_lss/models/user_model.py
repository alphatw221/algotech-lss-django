from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class User(db.Model):
    __tablename__ = "lss_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(50), unique=True, nullable=False)
    fb_user_email = db.Column(db.String(100), unique=True, nullable=True)
    fb_user_name = db.Column(db.String(50), nullable=True)
    fb_user_token = db.Column(db.String(200), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), nullable=True)
    date_added = db.Column(db.DateTime, nullable=True, default=datetime.now)
    update_time = db.Column(db.DateTime,
                            nullable=True, onupdate=datetime.now, default=datetime.now)

    def __init__(self,
                 fb_user_id,
                 fb_user_email,
                 fb_user_name,
                 fb_user_token,
                 company_name,
                 phone_number,
                 image,
                 ip,
                 status):

        self.fb_user_id = fb_user_id
        self.fb_user_email = fb_user_email
        self.fb_user_name = fb_user_name
        self.fb_user_token = fb_user_token
        self.company_name = company_name
        self.phone_number = phone_number
        self.image = image
        self.ip = ip
        self.status = status


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_user_id',
                  'fb_user_email',
                  'fb_user_name',
                  'company_name',
                  'phone_number',
                  'image',
                  'ip',
                  'status')

    fb_user_id = Str()
    fb_user_email = Str()
    fb_user_name = Str()
    company_name = Str()
    phone_number = Str()
    image = Str()
    ip = Str()
    status = Str()


class UserMeta(db.Model):
    __tablename__ = "lss_user_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(50), db.ForeignKey(
        "lss_user.fb_user_id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self,
                 fb_user_id,
                 meta_key,
                 meta_value):

        self.fb_user_id = fb_user_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class UserMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'fb_user_id',
                  'meta_key',
                  'meta_value')

        id = Integer()
        fb_user_id = Str()
        meta_key = Str()
        meta_value = Str()


class UserFBPage(db.Model):
    __tablename__ = "lss_user_fb_page"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(50), nullable=False)
    fb_page_id = db.Column(db.String(32),  nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self,
                 fb_user_id,
                 fb_page_id):

        self.fb_user_id = fb_user_id
        self.fb_page_id = fb_page_id


class UserFBPageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
            'fb_user_id',
            'fb_page_id',
            'created_at',
            'updated_at')

    fb_user_id = Str()
    fb_page_id = Str()
    created_at = DateTime()
    updated_at = DateTime()

