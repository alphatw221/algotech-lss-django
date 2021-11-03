from config import db, ma
from marshmallow.fields import *


class FBMessengerAutoResponse(db.Model):
    __tablename__ = "lss_fb_messenger_autoresponse"

    id = db.Column(db.Integer, primary_key=True)
    fb_page_id = db.Column(db.Text, nullable=False)
    message_req = db.Column(db.Text, nullable=False)
    message_res = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.Text, nullable=True)
    message_des = db.Column(db.Text, nullable=True)

    def __init__(self, fb_page_id, message_req, message_res, message_type, message_des):
        self.fb_page_id = fb_page_id
        self.message_req = message_req
        self.message_res = message_res
        self.message_type = message_type
        self.message_des = message_des


class FBMessengerAutoResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'fb_page_id', 'message_req',
                  'message_res', 'message_type', 'message_des')

        id = Integer()
        fb_page_id = Str()
        message_req = Str()
        message_res = Str()
        message_type = Str()
        message_des = Str()
