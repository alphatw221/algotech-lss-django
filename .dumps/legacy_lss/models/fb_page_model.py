from datetime import datetime
from config import db, ma
from marshmallow.fields import *


class FBPage(db.Model):
    __tablename__ = "lss_fb_page"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_page_id = db.Column(db.String(32),  unique=True, nullable=False)
    fb_page_name = db.Column(db.String(128), nullable=True)
    fb_page_token = db.Column(db.String(300), nullable=True)
    fb_page_token_updated_user = db.Column(db.String(50), nullable=True)
    fb_page_token_expires_in = db.Column(db.Integer(), nullable=True)
    fb_page_token_updated_time = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)
    lang = db.Column(db.String(8), nullable=False, default='')

    def __init__(self,
                 fb_page_id,
                 fb_page_name,
                 fb_page_token,
                 fb_page_token_updated_user,
                 fb_page_token_expires_in):
        self.fb_page_id = fb_page_id
        self.fb_page_name = fb_page_name
        self.fb_page_token = fb_page_token
        self.fb_page_token_updated_user = fb_page_token_updated_user
        self.fb_page_token_expires_in = fb_page_token_expires_in


class FBPageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_page_id',
                  'fb_page_name',
                  'fb_page_token_updated_user',
                  'fb_page_token_expires_in',
                  'fb_page_token_updated_time',
                  'lang')

        fb_page_id = Str()
        fb_page_name = Str()
        fb_page_token_updated_user = Str()
        fb_page_token_expires_in = Integer()
        fb_page_token_updated_time = DateTime()
        lang = Str()


class FBPageMeta(db.Model):
    __tablename__ = "lss_fb_page_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_page_id = db.Column(db.String(32), db.ForeignKey(
        "lss_fb_page.fb_page_id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self,
                 fb_page_id,
                 meta_key,
                 meta_value):

        self.fb_page_id = fb_page_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class FBPageMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'fb_page_id',
                  'meta_key',
                  'meta_value')

        id = Integer()
        fb_page_id = Integer()
        meta_key = Str()
        meta_value = Str()
