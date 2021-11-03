from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class UserPlan(db.Model):
    __tablename__ = "lss_user_plan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False, default='')
    excerpt = db.Column(db.Text, nullable=False, default='')
    content = db.Column(db.Text, nullable=False, default='')
    remark = db.Column(db.Text, nullable=False, default='')
    days = db.Column(db.Integer, nullable=False, default=0)
    limit_fb_pages = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(64), nullable=False, default='')
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    price_ori = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    image = db.Column(db.String(255), nullable=False, default='')
    sort_order = db.Column(db.Integer, nullable=True, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self,
                 title,
                 excerpt,
                 content,
                 remark,
                 days,
                 limit_fb_pages,
                 points,
                 status,
                 price,
                 price_ori,
                 image,
                 sort_order):
        self.title = title
        self.excerpt = excerpt
        self.content = content
        self.remark = remark
        self.days = days
        self.limit_fb_pages = limit_fb_pages
        self.points = points
        self.status = status
        self.price = price
        self.price_ori = price_ori
        self.image = image
        self.sort_order = sort_order


class UserPlanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
            'id',
            'title',
            'excerpt',
            'content',
            'remark',
            'days',
            'limit_fb_pages',
            'points',
            'status',
            'price',
            'price_ori',
            'image',
            'sort_order',
            'created_at',
            'updated_at')

    id = Integer()
    title = Str()
    excerpt = Str()
    content = Str()
    remark = Str()
    days = Integer()
    limit_fb_pages = Integer()
    points = Integer()
    status = Str()
    price = Decimal()
    price_ori = Decimal()
    image = Str()
    sort_order = Integer()
    created_at = DateTime()
    updated_at = DateTime()


class UserOrder(db.Model):
    __tablename__ = "lss_user_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(50), nullable=False, default='')
    fb_user_email = db.Column(db.String(100), nullable=False, default='')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    closed_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    plan_id = db.Column(db.Integer, nullable=False, default=0)
    days = db.Column(db.Integer, nullable=False, default=0)
    limit_fb_pages = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)
    points_left = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self,
                 fb_user_id,
                 fb_user_email,
                 created_at,
                 updated_at,
                 closed_at,
                 plan_id,
                 days,
                 limit_fb_pages,
                 points,
                 points_left):

        self.fb_user_id = fb_user_id
        self.fb_user_email = fb_user_email
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at
        self.plan_id = plan_id
        self.days = days
        self.limit_fb_pages = limit_fb_pages
        self.points = points
        self.points_left = points_left


class UserOrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
            'id',
            'fb_user_id',
            'fb_user_email',
            'created_at',
            'updated_at',
            'closed_at',
            'plan_id',
            'days',
            'limit_fb_pages',
            'points',
            'points_left',
        )

    id = Integer()
    fb_user_id = Str()
    fb_user_email = Str()
    created_at = DateTime()
    updated_at = DateTime()
    closed_at = DateTime()
    plan_id = Integer()
    days = Integer()
    limit_fb_pages = Integer()
    points = Integer()
    points_left = Integer()


class UserOrderMeta(db.Model):
    __tablename__ = "lss_user_order_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_order_id = db.Column(db.Integer, db.ForeignKey(
        "lss_user_order.id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self, user_order_id, meta_key, meta_value):

        self.user_order_id = user_order_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class UserOrderMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'user_order_id', 'meta_key', 'meta_value')

        id = Integer()
        user_order_id = Integer()
        meta_key = Str()
        meta_value = Str()


class UserAccess(db.Model):
    __tablename__ = "lss_user_access"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(255), nullable=False, default='')
    item_id = db.Column(db.String(255), nullable=False, default='')
    type = db.Column(db.String(255), nullable=False, default='')
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    remark = db.Column(db.Text, nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint(fb_user_id, item_id),
    )

    def __init__(self,
                 fb_user_id,
                 item_id,
                 type,
                 start_date,
                 end_date,
                 remark):
        self.fb_user_id = fb_user_id
        self.item_id = item_id
        self.type = type
        self.start_date = start_date
        self.end_date = end_date
        self.remark = remark


class UserAccessSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
            'id',
            'fb_user_id',
            'item_id',
            'type',
            'start_date',
            'end_date',
            'remark')

    id = Integer()
    fb_user_id = Str()
    item_id = Str()
    type = Str()
    start_date = DateTime()
    end_date = DateTime()
    remark = Str()
