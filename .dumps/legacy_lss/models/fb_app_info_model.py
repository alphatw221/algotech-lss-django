from config import db, ma
from marshmallow.fields import *


class FBAppInfo(db.Model):
    __tablename__ = "lss_fb_app_info"

    id = db.Column(db.Integer, primary_key=True)
    app_type = db.Column(db.Text, nullable=True)
    fb_app_id = db.Column(db.Text, nullable=True)
    fb_app_secret = db.Column(db.Text, nullable=True)
    fb_app_name = db.Column(db.Text, nullable=True)

    def __init__(self, fb_app_id):
        self.fb_app_id = fb_app_id


class FBAppInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'app_type',
                  'fb_app_id',
                  'fb_app_secret',
                  'fb_app_name')

        id = Integer()
        app_type = Str()
        fb_app_id = Str()
        fb_app_secret = Str()
        fb_app_name = Str()
